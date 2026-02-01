"""Google Maps API integration using Places API (New) and Routes API"""
import requests
import os
from config import VIBE_CONFIGS, ALL_DISCOVERABLE_TYPES
from utils.geo_utils import calculate_distance

# Get API key from environment
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# API endpoints
PLACES_NEARBY_URL = "https://places.googleapis.com/v1/places:searchNearby"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"


def geocode_location(api_key, location_name):
    """
    Geocode a location name to coordinates using Geocoding API.
    Returns dict with latitude, longitude, and formatted_address, or None if not found.
    """
    if not api_key or not location_name:
        return None

    try:
        response = requests.get(
            GEOCODE_URL,
            params={
                'address': location_name,
                'key': api_key
            },
            timeout=10
        )

        data = response.json()

        if data.get('status') != 'OK' or not data.get('results'):
            print(f"Geocoding: No results for '{location_name}' - Status: {data.get('status')}")
            if data.get('error_message'):
                print(f"Error: {data.get('error_message')}")
            return None

        result = data['results'][0]
        location = result['geometry']['location']

        return {
            'latitude': location['lat'],
            'longitude': location['lng'],
            'formatted_address': result['formatted_address'],
            'place_id': result.get('place_id')
        }

    except Exception as e:
        print(f"Geocoding error for '{location_name}': {e}")
        return None


def search_nearby_places(api_key, lat, lon, radius, included_types):
    """
    Search for nearby places using Places API (New).

    Args:
        api_key: Google Maps API key
        lat: Center latitude
        lon: Center longitude
        radius: Search radius in meters
        included_types: List of place types to search for

    Returns:
        List of place dictionaries
    """
    if not api_key:
        return []

    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': 'places.id,places.displayName,places.location,places.rating,places.userRatingCount,places.formattedAddress,places.types,places.primaryType'
    }

    body = {
        'includedTypes': included_types,
        'maxResultCount': 20,
        'locationRestriction': {
            'circle': {
                'center': {
                    'latitude': lat,
                    'longitude': lon
                },
                'radius': min(radius, 50000)  # Max 50km
            }
        }
    }

    try:
        response = requests.post(
            PLACES_NEARBY_URL,
            headers=headers,
            json=body,
            timeout=15
        )

        if response.status_code != 200:
            print(f"Places API error: {response.status_code} - {response.text}")
            return []

        data = response.json()
        places = []

        for place in data.get('places', []):
            location = place.get('location', {})
            places.append({
                'place_id': place.get('id'),
                'name': place.get('displayName', {}).get('text', 'Unknown'),
                'latitude': location.get('latitude'),
                'longitude': location.get('longitude'),
                'rating': place.get('rating', 0),
                'user_ratings_total': place.get('userRatingCount', 0),
                'address': place.get('formattedAddress', ''),
                'google_type': place.get('primaryType', included_types[0] if included_types else 'unknown'),
                'types': place.get('types', [])
            })

        return places

    except Exception as e:
        print(f"Error searching nearby places: {e}")
        return []


def get_google_places(api_key, lat, lon, vibe, radius):
    """Fetch nearby places for a specific vibe using Places API (New)."""
    if not api_key:
        return []

    vibe_config = VIBE_CONFIGS[vibe]
    google_types = vibe_config.get('google_types', [])

    if not google_types:
        return []

    # Search for all vibe types at once
    all_places = search_nearby_places(api_key, lat, lon, radius, google_types)

    # Calculate distance and filter
    result_places = []
    for place in all_places:
        if place['latitude'] and place['longitude']:
            distance = calculate_distance(lat, lon, place['latitude'], place['longitude'])
            rating = place.get('rating', 0)

            # Filter: must have rating >= 3.5 or be park
            if rating >= 3.5 or place.get('google_type') in ['park']:
                place['distance'] = distance
                place['type'] = place.get('google_type')
                result_places.append(place)

    # Sort by combination of rating and proximity
    result_places.sort(
        key=lambda x: (x.get('rating', 0) * 0.7 + (5000 - min(x.get('distance', 5000), 5000)) / 5000 * 0.3),
        reverse=True
    )

    return result_places[:20]


def discover_all_places(api_key, lat, lon, radius):
    """
    Fetch ALL place types in the area using Places API (New).
    Returns list of unique places (deduped by place_id).
    """
    if not api_key:
        print("No API key provided for discover_all_places")
        return []

    seen_ids = set()
    all_places = []

    # Batch types into groups to reduce API calls (max 50 types per request)
    batch_size = 50
    type_batches = [ALL_DISCOVERABLE_TYPES[i:i+batch_size] for i in range(0, len(ALL_DISCOVERABLE_TYPES), batch_size)]

    for type_batch in type_batches:
        try:
            places = search_nearby_places(api_key, lat, lon, radius, type_batch)

            for place in places:
                place_id = place.get('place_id')
                if not place_id or place_id in seen_ids:
                    continue

                seen_ids.add(place_id)

                # Calculate distance
                if place.get('latitude') and place.get('longitude'):
                    place['distance'] = calculate_distance(lat, lon, place['latitude'], place['longitude'])

                all_places.append(place)

        except Exception as e:
            print(f"Error fetching places batch: {e}")
            continue

    print(f"Discovered {len(all_places)} unique places")
    return all_places


def get_google_directions(api_key, waypoints):
    """Get walking route using Directions API."""
    if not api_key or len(waypoints) < 2:
        return None

    origin = waypoints[0]
    destination = waypoints[-1]
    intermediates = waypoints[1:-1] if len(waypoints) > 2 else []

    params = {
        'origin': f'{origin[0]},{origin[1]}',
        'destination': f'{destination[0]},{destination[1]}',
        'mode': 'walking',
        'units': 'metric',
        'key': api_key
    }

    # Add waypoints if any
    if intermediates:
        waypoints_str = '|'.join([f'{wp[0]},{wp[1]}' for wp in intermediates])
        params['waypoints'] = waypoints_str

    try:
        response = requests.get(DIRECTIONS_URL, params=params, timeout=15)
        data = response.json()

        if data.get('status') != 'OK':
            print(f"Directions API error: {data.get('status')} - {data.get('error_message', '')}")
            return None

        if not data.get('routes'):
            print("No routes returned")
            return None

        route = data['routes'][0]
        leg_data = route['legs']

        # Decode polyline to coordinates
        encoded_polyline = route.get('overview_polyline', {}).get('points', '')
        coordinates = decode_polyline(encoded_polyline)

        # Calculate totals
        total_distance = sum(leg['distance']['value'] for leg in leg_data)
        total_duration = sum(leg['duration']['value'] for leg in leg_data) // 60

        # Extract steps
        steps = []
        for leg in leg_data:
            for step in leg['steps']:
                instruction = step.get('html_instructions', 'Continue')
                # Clean HTML tags
                instruction = instruction.replace('<b>', '').replace('</b>', '')
                instruction = instruction.replace('<div style="font-size:0.9em">', ' - ').replace('</div>', '')

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
            'polyline': encoded_polyline
        }

    except Exception as e:
        print(f"Directions error: {e}")
        import traceback
        traceback.print_exc()
        return None


def decode_polyline(encoded):
    """Decode a Google encoded polyline string into a list of [lng, lat] coordinates."""
    if not encoded:
        return []

    decoded = []
    index = 0
    lat = 0
    lng = 0

    while index < len(encoded):
        # Decode latitude
        shift = 0
        result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        lat += (~(result >> 1) if result & 1 else result >> 1)

        # Decode longitude
        shift = 0
        result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        lng += (~(result >> 1) if result & 1 else result >> 1)

        decoded.append([lng / 1e5, lat / 1e5])

    return decoded
