"""Google Maps API integration"""
import googlemaps
from config import VIBE_CONFIGS, ALL_DISCOVERABLE_TYPES
from utils.geo_utils import calculate_distance


def geocode_location(gmaps_client, location_name):
    """
    Geocode a location name to coordinates
    Returns dict with latitude, longitude, and formatted_address, or None if not found
    """
    if not gmaps_client or not location_name:
        return None

    try:
        # Add country bias for better results (can be made configurable)
        geocode_result = gmaps_client.geocode(location_name)

        if not geocode_result:
            print(f"Geocoding: No results found for '{location_name}'")
            return None

        result = geocode_result[0]
        location = result['geometry']['location']

        return {
            'latitude': location['lat'],
            'longitude': location['lng'],
            'formatted_address': result['formatted_address'],
            'place_id': result.get('place_id')
        }

    except Exception as e:
        print(f"Geocoding error for '{location_name}': {e}")
        # Check if it's an API permission error
        if 'REQUEST_DENIED' in str(e):
            print("ERROR: Geocoding API not enabled. Please enable it in Google Cloud Console.")
        return None


def get_google_places(gmaps_client, lat, lon, vibe, radius):
    """Fetch nearby places using Google Places API"""
    if not gmaps_client:
        return []

    vibe_config = VIBE_CONFIGS[vibe]
    google_types = vibe_config.get('google_types', [])

    all_places = []

    for place_type in google_types:
        try:
            results = gmaps_client.places_nearby(
                location=(lat, lon),
                radius=radius,
                type=place_type
            )

            for place in results.get('results', [])[:5]:  # Top 5 per type
                # Filter: must have rating >= 3.5 or be park/natural feature
                rating = place.get('rating', 0)
                if rating >= 3.5 or place_type in ['park', 'natural_feature']:
                    location = place['geometry']['location']
                    distance = calculate_distance(lat, lon, location['lat'], location['lng'])
                    all_places.append({
                        'name': place.get('name'),
                        'type': place_type,
                        'latitude': location['lat'],
                        'longitude': location['lng'],
                        'rating': rating,
                        'user_ratings_total': place.get('user_ratings_total', 0),
                        'address': place.get('vicinity', ''),
                        'place_id': place.get('place_id'),
                        'distance': distance
                    })
        except Exception as e:
            print(f"Error fetching {place_type}: {e}")
            continue

    # Sort by combination of rating and proximity
    all_places.sort(
        key=lambda x: (x['rating'] * 0.7 + (5000 - min(x['distance'], 5000)) / 5000 * 0.3),
        reverse=True
    )

    return all_places[:20]  # Return top 20


def get_google_directions(gmaps_client, waypoints):
    """Get walking route from Google Directions API"""
    if not gmaps_client or len(waypoints) < 2:
        return None

    origin = waypoints[0]
    destination = waypoints[-1]
    intermediate = waypoints[1:-1] if len(waypoints) > 2 else None

    try:
        directions_result = gmaps_client.directions(
            origin=origin,
            destination=destination,
            waypoints=intermediate,
            mode="walking",
            units="metric",
            alternatives=False
        )

        if not directions_result:
            return None

        route = directions_result[0]
        leg_data = route['legs']

        # Extract route coordinates from polylines
        coordinates = []
        for leg in leg_data:
            for step in leg['steps']:
                # Decode polyline - Google returns it as an encoded string
                polyline_points = googlemaps.convert.decode_polyline(step['polyline']['points'])
                coordinates.extend([[point['lng'], point['lat']] for point in polyline_points])

        # Calculate totals
        total_distance = sum(leg['distance']['value'] for leg in leg_data)
        total_duration = sum(leg['duration']['value'] for leg in leg_data) // 60  # Convert to minutes

        # Extract turn-by-turn steps
        steps = []
        for leg in leg_data:
            for step in leg['steps']:
                # Clean HTML tags from instructions
                instruction = step['html_instructions'].replace('<b>', '').replace('</b>', '').replace('<div style="font-size:0.9em">', ' - ').replace('</div>', '')
                steps.append({
                    'instruction': instruction,
                    'distance': step['distance']['value'],
                    'duration': step['duration']['value'] // 60,
                    'maneuver': step.get('maneuver', 'straight')
                })

        return {
            'coordinates': coordinates,
            'distance': total_distance,
            'duration': total_duration,
            'steps': steps,
            'polyline': route['overview_polyline']['points']
        }

    except Exception as e:
        print(f"Directions error: {e}")
        return None


def discover_all_places(gmaps_client, lat, lon, radius):
    """
    Fetch ALL place types in the area.
    Returns list of unique places (deduped by place_id).

    Args:
        gmaps_client: Google Maps client instance
        lat: Center latitude
        lon: Center longitude
        radius: Search radius in meters

    Returns:
        List of place dictionaries with deduplication by place_id
    """
    if not gmaps_client:
        return []

    seen_ids = set()
    all_places = []

    for place_type in ALL_DISCOVERABLE_TYPES:
        try:
            results = gmaps_client.places_nearby(
                location=(lat, lon),
                radius=radius,
                type=place_type
            )

            for place in results.get('results', []):
                place_id = place['place_id']

                # Skip if already seen
                if place_id in seen_ids:
                    continue

                seen_ids.add(place_id)
                location = place['geometry']['location']

                all_places.append({
                    'place_id': place_id,
                    'name': place.get('name'),
                    'google_type': place_type,
                    'latitude': location['lat'],
                    'longitude': location['lng'],
                    'rating': place.get('rating', 0),
                    'user_ratings_total': place.get('user_ratings_total', 0),
                    'address': place.get('vicinity', '')
                })

        except Exception as e:
            print(f"Error fetching places of type {place_type}: {e}")
            continue

    return all_places
