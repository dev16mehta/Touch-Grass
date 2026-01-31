from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import json
import random

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

MAPBOX_TOKEN = os.getenv('MAPBOX_TOKEN')

# Vibe configurations
VIBE_CONFIGS = {
    'chill': {
        'emoji': '🌿',
        'description': 'Relaxing walk with parks and quiet spots',
        'place_types': ['park', 'cafe', 'garden'],
        'pace': 'slow',
        'noise_preference': 'quiet'
    },
    'date': {
        'emoji': '💕',
        'description': 'Romantic walk with cafes and scenic views',
        'place_types': ['cafe', 'restaurant', 'park', 'viewpoint'],
        'pace': 'moderate',
        'noise_preference': 'moderate'
    },
    'chaos': {
        'emoji': '🍻',
        'description': 'Energetic walk with bars and nightlife',
        'place_types': ['bar', 'pub', 'restaurant', 'entertainment'],
        'pace': 'fast',
        'noise_preference': 'lively'
    },
    'aesthetic': {
        'emoji': '📸',
        'description': 'Instagram-worthy spots and scenic views',
        'place_types': ['viewpoint', 'park', 'landmark', 'cafe'],
        'pace': 'slow',
        'noise_preference': 'any'
    }
}


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Touch Grass API is running!'})


@app.route('/api/vibes', methods=['GET'])
def get_vibes():
    """Get available vibes"""
    return jsonify({
        'vibes': [
            {'id': key, 'name': key.capitalize(), 'emoji': config['emoji'], 'description': config['description']}
            for key, config in VIBE_CONFIGS.items()
        ]
    })


@app.route('/api/generate-route', methods=['POST'])
def generate_route():
    """Generate a walking route based on vibe and location"""
    try:
        data = request.json
        vibe = data.get('vibe', 'chill')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        radius = data.get('radius', 2000)  # 2km default

        if not latitude or not longitude:
            return jsonify({'error': 'Location (latitude, longitude) is required'}), 400

        if vibe not in VIBE_CONFIGS:
            return jsonify({'error': f'Invalid vibe. Choose from: {list(VIBE_CONFIGS.keys())}'}), 400

        # Get nearby places from Mapbox
        places = get_nearby_places(latitude, longitude, vibe, radius)

        # Generate route waypoints
        route_points = generate_route_waypoints(latitude, longitude, places, vibe)

        # Get AI-enhanced description
        description = get_ai_description(vibe, places)

        return jsonify({
            'vibe': vibe,
            'description': description,
            'route': route_points,
            'places': places[:10],  # Return top 10 places
            'config': VIBE_CONFIGS[vibe]
        })

    except Exception as e:
        print(f"Error generating route: {str(e)}")
        return jsonify({'error': str(e)}), 500


def get_nearby_places(lat, lon, vibe, radius):
    """Fetch nearby places using Mapbox Geocoding API"""
    vibe_config = VIBE_CONFIGS[vibe]
    place_types = vibe_config['place_types']

    all_places = []

    # Map our place types to Mapbox categories
    mapbox_categories = {
        'park': 'park,natural_feature',
        'cafe': 'cafe,coffee',
        'restaurant': 'restaurant',
        'bar': 'bar',
        'pub': 'bar,nightlife',
        'garden': 'park,natural_feature',
        'viewpoint': 'natural_feature,landmark',
        'landmark': 'landmark,tourist_attraction',
        'entertainment': 'nightlife,entertainment'
    }

    for place_type in place_types:
        categories = mapbox_categories.get(place_type, place_type)

        # Use Mapbox Geocoding API to search for places
        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{place_type}.json"
        params = {
            'proximity': f"{lon},{lat}",
            'limit': 10,
            'access_token': MAPBOX_TOKEN
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            for feature in data.get('features', []):
                coords = feature['geometry']['coordinates']
                all_places.append({
                    'name': feature.get('text', 'Unknown'),
                    'type': place_type,
                    'latitude': coords[1],
                    'longitude': coords[0],
                    'address': feature.get('place_name', ''),
                    'distance': calculate_distance(lat, lon, coords[1], coords[0])
                })

    # Sort by distance
    all_places.sort(key=lambda x: x['distance'])
    return all_places


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate approximate distance in meters"""
    from math import radians, sin, cos, sqrt, atan2

    R = 6371000  # Earth's radius in meters

    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c


def generate_route_waypoints(start_lat, start_lon, places, vibe):
    """Generate a walking route through interesting places"""
    if not places:
        # Return a simple circular route if no places found
        return create_circular_route(start_lat, start_lon)

    # Select 3-5 waypoints based on vibe
    num_waypoints = 4 if vibe in ['chaos', 'aesthetic'] else 3
    selected_places = places[:num_waypoints]

    # Create route: start -> places -> back to start
    waypoints = [[start_lon, start_lat]]

    for place in selected_places:
        waypoints.append([place['longitude'], place['latitude']])

    # Add return to start
    waypoints.append([start_lon, start_lat])

    return waypoints


def create_circular_route(lat, lon, radius=0.01):
    """Create a simple circular route"""
    import math
    waypoints = [[lon, lat]]

    for i in range(4):
        angle = (i * 90) * (math.pi / 180)
        new_lat = lat + radius * math.cos(angle)
        new_lon = lon + radius * math.sin(angle)
        waypoints.append([new_lon, new_lat])

    waypoints.append([lon, lat])
    return waypoints


def get_ai_description(vibe, places):
    """Generate AI-powered route description using Gemini"""
    try:
        vibe_config = VIBE_CONFIGS[vibe]
        place_names = [p['name'] for p in places[:5]]

        prompt = f"""Generate a short, exciting description (2-3 sentences) for a {vibe} walking route.

Vibe: {vibe} {vibe_config['emoji']} - {vibe_config['description']}
Places on route: {', '.join(place_names) if place_names else 'local area'}

Make it fun, casual, and match the vibe. Keep it under 50 words."""

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print(f"AI description error: {e}")
        return f"A {vibe} walk through the local area. {vibe_config['description']}."


@app.route('/api/get-directions', methods=['POST'])
def get_directions():
    """Get walking directions between waypoints using Mapbox Directions API"""
    try:
        data = request.json
        waypoints = data.get('waypoints', [])

        if len(waypoints) < 2:
            return jsonify({'error': 'At least 2 waypoints required'}), 400

        # Format coordinates for Mapbox API
        coordinates = ';'.join([f"{wp[0]},{wp[1]}" for wp in waypoints])

        url = f"https://api.mapbox.com/directions/v5/mapbox/walking/{coordinates}"
        params = {
            'geometries': 'geojson',
            'overview': 'full',
            'steps': 'true',
            'access_token': MAPBOX_TOKEN
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Failed to get directions'}), 500

    except Exception as e:
        print(f"Directions error: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
