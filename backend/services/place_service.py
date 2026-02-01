"""Place service for managing place storage, retrieval, and categorization"""
from typing import List, Tuple, Optional, Dict, Any
from models.database import get_db
from models.place import Place
from config import PLACE_TYPE_TO_VIBES
from services.ai_service import categorize_place_with_llm
from utils.geo_utils import calculate_distance


def save_place(place_data: dict, vibes: List[str], source: str = 'static') -> None:
    """
    Insert or update a place and its vibe associations.

    Args:
        place_data: Dictionary with place information
        vibes: List of vibe strings the place belongs to
        source: 'static' or 'llm' indicating how vibes were determined
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Insert or replace place
        cursor.execute('''
            INSERT OR REPLACE INTO places
            (place_id, name, latitude, longitude, google_type, address, rating, user_ratings_total, categorization_source, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            place_data['place_id'],
            place_data['name'],
            place_data['latitude'],
            place_data['longitude'],
            place_data.get('google_type'),
            place_data.get('address'),
            place_data.get('rating'),
            place_data.get('user_ratings_total'),
            source
        ))

        # Delete existing vibe associations
        cursor.execute('DELETE FROM place_vibes WHERE place_id = ?', (place_data['place_id'],))

        # Insert new vibe associations
        for vibe in vibes:
            cursor.execute(
                'INSERT OR IGNORE INTO place_vibes (place_id, vibe) VALUES (?, ?)',
                (place_data['place_id'], vibe)
            )


def save_places_bulk(places_with_vibes: List[Tuple[dict, List[str], str]]) -> None:
    """
    Batch insert multiple places with their vibes.

    Args:
        places_with_vibes: List of tuples (place_data, vibes, source)
    """
    with get_db() as conn:
        cursor = conn.cursor()

        for place_data, vibes, source in places_with_vibes:
            # Insert or replace place
            cursor.execute('''
                INSERT OR REPLACE INTO places
                (place_id, name, latitude, longitude, google_type, address, rating, user_ratings_total, categorization_source, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                place_data['place_id'],
                place_data['name'],
                place_data['latitude'],
                place_data['longitude'],
                place_data.get('google_type'),
                place_data.get('address'),
                place_data.get('rating'),
                place_data.get('user_ratings_total'),
                source
            ))

            # Delete existing vibe associations
            cursor.execute('DELETE FROM place_vibes WHERE place_id = ?', (place_data['place_id'],))

            # Insert new vibe associations
            for vibe in vibes:
                cursor.execute(
                    'INSERT OR IGNORE INTO place_vibes (place_id, vibe) VALUES (?, ?)',
                    (place_data['place_id'], vibe)
                )


def get_places_by_vibe(lat: float, lon: float, radius: float, vibe: str) -> List[dict]:
    """
    Query places that belong to a specific vibe within a radius.

    Args:
        lat: Center latitude
        lon: Center longitude
        radius: Search radius in meters
        vibe: Vibe to filter by

    Returns:
        List of place dictionaries with distance calculated
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Get all places that have the requested vibe
        cursor.execute('''
            SELECT DISTINCT p.place_id, p.name, p.latitude, p.longitude, p.google_type,
                   p.address, p.rating, p.user_ratings_total, p.categorization_source
            FROM places p
            JOIN place_vibes pv ON p.place_id = pv.place_id
            WHERE pv.vibe = ?
        ''', (vibe,))

        rows = cursor.fetchall()
        places = []

        for row in rows:
            # Calculate distance
            distance = calculate_distance(lat, lon, row['latitude'], row['longitude'])

            # Filter by radius
            if distance <= radius:
                # Get all vibes for this place
                cursor.execute(
                    'SELECT vibe FROM place_vibes WHERE place_id = ?',
                    (row['place_id'],)
                )
                vibes = [v['vibe'] for v in cursor.fetchall()]

                places.append({
                    'place_id': row['place_id'],
                    'name': row['name'],
                    'latitude': row['latitude'],
                    'longitude': row['longitude'],
                    'type': row['google_type'],
                    'google_type': row['google_type'],
                    'address': row['address'],
                    'rating': row['rating'] or 0,
                    'user_ratings_total': row['user_ratings_total'] or 0,
                    'categorization_source': row['categorization_source'],
                    'vibes': vibes,
                    'distance': distance
                })

        # Sort by rating (all vibe members are equal, so just use rating)
        places.sort(key=lambda x: x['rating'], reverse=True)

        return places


def get_vibes_for_place(place_id: str) -> List[str]:
    """Get all vibes associated with a place."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT vibe FROM place_vibes WHERE place_id = ?', (place_id,))
        return [row['vibe'] for row in cursor.fetchall()]


def categorize_place(place: dict, openrouter_api_key: str = None) -> Tuple[List[str], str]:
    """
    Categorize a place into vibes.
    Uses static mapping if type is known, otherwise calls LLM.

    Args:
        place: Place dictionary with at least 'name' and 'google_type' or 'type'
        openrouter_api_key: API key for LLM fallback

    Returns:
        Tuple of (vibes list, source string)
    """
    place_type = place.get('google_type') or place.get('type')

    # Try static mapping first
    if place_type and place_type in PLACE_TYPE_TO_VIBES:
        vibes = PLACE_TYPE_TO_VIBES[place_type]
        if vibes:  # Only use static if it has mappings
            return vibes, 'static'

    # Unknown type or empty static mapping - use LLM
    if openrouter_api_key:
        vibes = categorize_place_with_llm(
            openrouter_api_key,
            place.get('name', 'Unknown'),
            place_type or 'unknown'
        )
        if vibes:
            return vibes, 'llm'

    # Fallback: return empty vibes
    return [], 'static'


def is_area_indexed(lat: float, lon: float, radius: float, tolerance: float = 0.5) -> bool:
    """
    Check if an area has already been indexed.

    Uses a tolerance factor to determine overlap. If an existing indexed area
    covers most of the requested area, returns True.

    Args:
        lat: Center latitude
        lon: Center longitude
        radius: Search radius in meters
        tolerance: Fraction of radius that must overlap (0.5 = 50%)

    Returns:
        True if area is sufficiently indexed
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Get all indexed areas
        cursor.execute('SELECT center_lat, center_lon, radius FROM indexed_areas')
        areas = cursor.fetchall()

        for area in areas:
            # Calculate distance between centers
            center_distance = calculate_distance(lat, lon, area['center_lat'], area['center_lon'])

            # If the new area's center is within the old area's radius,
            # and the old area's radius is >= the new radius * tolerance,
            # consider it indexed
            if center_distance <= area['radius'] and area['radius'] >= radius * tolerance:
                return True

        return False


def mark_area_indexed(lat: float, lon: float, radius: float) -> None:
    """Mark an area as indexed."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO indexed_areas (center_lat, center_lon, radius) VALUES (?, ?, ?)',
            (lat, lon, radius)
        )


def get_place_by_id(place_id: str) -> Optional[dict]:
    """Get a single place by its ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT place_id, name, latitude, longitude, google_type,
                   address, rating, user_ratings_total, categorization_source
            FROM places WHERE place_id = ?
        ''', (place_id,))

        row = cursor.fetchone()
        if not row:
            return None

        # Get vibes
        cursor.execute('SELECT vibe FROM place_vibes WHERE place_id = ?', (place_id,))
        vibes = [v['vibe'] for v in cursor.fetchall()]

        return {
            'place_id': row['place_id'],
            'name': row['name'],
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'google_type': row['google_type'],
            'address': row['address'],
            'rating': row['rating'],
            'user_ratings_total': row['user_ratings_total'],
            'categorization_source': row['categorization_source'],
            'vibes': vibes
        }
