"""Flask API for Touch Grass - Mood-based walking routes"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai
import googlemaps

from config import VIBE_CONFIGS
from services.ai_service import detect_vibe_from_text, generate_route_description
from services.google_maps_service import get_google_places, get_google_directions
from services.route_service import calculate_route_parameters, optimize_waypoints

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
gemini_model = genai.GenerativeModel('gemini-pro')

# Configure Google Maps
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY) if GOOGLE_MAPS_API_KEY else None

# API Keys
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'google_maps_configured': gmaps is not None,
        'gemini_configured': os.getenv('GEMINI_API_KEY') is not None,
        'openrouter_configured': OPENROUTER_API_KEY is not None
    })


@app.route('/api/vibes', methods=['GET'])
def get_vibes():
    """Get all available vibes"""
    return jsonify({
        'vibes': [
            {
                'id': key,
                'name': key.capitalize(),
                'emoji': config['emoji'],
                'description': config['description']
            }
            for key, config in VIBE_CONFIGS.items()
        ]
    })


@app.route('/api/detect-vibe', methods=['POST'])
def detect_vibe():
    """Detect vibe from user's text description using LLM"""
    try:
        data = request.json
        user_text = data.get('text', '').strip()

        if not user_text:
            return jsonify({'error': 'Text description is required'}), 400

        result = detect_vibe_from_text(OPENROUTER_API_KEY, user_text)
        return jsonify(result)

    except ValueError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        print(f"Error detecting vibe: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-route', methods=['POST'])
def generate_route():
    """Generate a walking route based on vibe, location, duration, and route type"""
    try:
        data = request.json
        vibe = data.get('vibe', 'chill')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        duration = data.get('duration', 30)
        is_circular = data.get('circular', True)

        # Validate inputs
        if not latitude or not longitude:
            return jsonify({'error': 'Location (latitude, longitude) is required'}), 400

        if vibe not in VIBE_CONFIGS:
            return jsonify({'error': f'Invalid vibe. Choose from: {list(VIBE_CONFIGS.keys())}'}), 400

        if not gmaps:
            return jsonify({'error': 'Google Maps API not configured'}), 500

        if duration < 10 or duration > 120:
            return jsonify({'error': 'Duration must be between 10 and 120 minutes'}), 400

        # Calculate route parameters
        route_params = calculate_route_parameters(duration, vibe, is_circular)
        search_radius = route_params['search_radius']

        # Get nearby places
        places = get_google_places(gmaps, latitude, longitude, vibe, search_radius)

        # If no places found, expand search radius
        if not places:
            places = get_google_places(gmaps, latitude, longitude, vibe, min(search_radius * 2, 10000))

        # Optimize waypoints
        waypoints = optimize_waypoints(
            latitude, longitude, places.copy(),
            route_params['target_distance'], vibe, is_circular
        )

        # Get directions
        directions = get_google_directions(gmaps, waypoints)

        if not directions:
            return jsonify({'error': 'Could not generate route. Try a different location or duration.'}), 500

        # Generate AI description
        description = generate_route_description(gemini_model, vibe, places)

        return jsonify({
            'vibe': vibe,
            'description': description,
            'route': {
                'coordinates': directions['coordinates'],
                'distance': directions['distance'],
                'duration': directions['duration'],
                'polyline': directions['polyline']
            },
            'waypoints': places[:10],
            'directions': {
                'steps': directions['steps']
            },
            'config': VIBE_CONFIGS[vibe]
        })

    except Exception as e:
        print(f"Error generating route: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
