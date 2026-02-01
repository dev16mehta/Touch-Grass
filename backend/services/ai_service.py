"""AI service for LLM integrations (OpenRouter and Gemini)"""
import requests
import json
import os
from config import VIBE_CONFIGS, VALID_VIBES


def detect_vibe_from_text(openrouter_api_key, user_text):
    """Detect vibe and location from user's text description using OpenRouter LLM"""
    if not openrouter_api_key:
        raise ValueError('OpenRouter API not configured')

    headers = {
        'Authorization': f'Bearer {openrouter_api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'http://localhost:5001',
        'X-Title': 'Touch Grass'
    }

    prompt = f"""You are a mood and location classifier for a walking route app.

Based on the user's description:
1. Classify their mood into ONE of these vibes: chill, date, chaos, or aesthetic
2. Extract any location mentioned (city, neighborhood, area name)

Vibes:
- "chill" - Relaxing, peaceful, quiet, wanting to unwind, destress, calm, meditative
- "date" - Romantic, with partner, coffee date, scenic, intimate, quality time
- "chaos" - Party, energetic, nightlife, bars, adventure, wild, exciting
- "aesthetic" - Photography, Instagram, beautiful views, artistic, scenic spots, pictures

User says: "{user_text}"

Respond in this EXACT format (nothing else):
vibe: [vibe_name]
location: [location_name or "none"]

Examples:
- "I want to relax in Central Park" → vibe: chill, location: Central Park
- "Date night in Kensington tonight" → vibe: date, location: Kensington
- "I'm feeling stressed" → vibe: chill, location: none
- "Party time in Shoreditch!" → vibe: chaos, location: Shoreditch"""

    payload = {
        'model': 'openai/gpt-3.5-turbo',
        'messages': [
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.3,
        'max_tokens': 50
    }

    response = requests.post(
        'https://openrouter.ai/api/v1/chat/completions',
        headers=headers,
        json=payload,
        timeout=10
    )

    if response.status_code != 200:
        print(f"OpenRouter API error: {response.text}")
        raise Exception('Failed to detect vibe from OpenRouter API')

    result = response.json()
    llm_response = result['choices'][0]['message']['content'].strip().lower()

    # Parse response
    detected_vibe = 'chill'  # Default
    detected_location = None

    for line in llm_response.split('\n'):
        if 'vibe:' in line:
            vibe = line.split('vibe:')[1].strip()
            if vibe in VIBE_CONFIGS:
                detected_vibe = vibe
        elif 'location:' in line:
            loc = line.split('location:')[1].strip()
            if loc and loc != 'none':
                detected_location = loc

    return {
        'vibe': detected_vibe,
        'emoji': VIBE_CONFIGS[detected_vibe]['emoji'],
        'description': VIBE_CONFIGS[detected_vibe]['description'],
        'location': detected_location
    }


def generate_route_description(gemini_model, vibe, places):
    """Generate AI-enhanced description using Gemini"""
    if not places:
        vibe_config = VIBE_CONFIGS.get(vibe, {})
        return vibe_config.get('description', 'A nice walking route')

    place_names = [p['name'] for p in places[:5]]
    vibe_config = VIBE_CONFIGS[vibe]

    prompt = f"""Create a brief, engaging description (2-3 sentences) for a {vibe} walk that passes by these places: {', '.join(place_names)}.
    The vibe is: {vibe_config['description']}.
    Make it sound inviting and match the {vibe} mood."""

    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API error: {e}")
        return vibe_config['description']


def categorize_place_with_llm(openrouter_api_key, place_name, place_type):
    """
    Use LLM to categorize a place that doesn't match predefined types.
    Returns list of vibes: ['chill', 'aesthetic'] etc.
    """
    if not openrouter_api_key:
        # Fallback: return empty vibes if no API key
        return []

    headers = {
        'Authorization': f'Bearer {openrouter_api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'http://localhost:5001',
        'X-Title': 'Touch Grass'
    }

    prompt = f"""Categorize this place for a walking route app.
Place: {place_name}
Google type: {place_type}

Available vibes:
- chill: peaceful, quiet, relaxing (parks, gardens, libraries)
- date: romantic, intimate, scenic (cafes, restaurants, viewpoints)
- chaos: energetic, nightlife, lively (bars, clubs, pubs)
- aesthetic: beautiful, photogenic, cultural (landmarks, museums, historic sites)

A place can belong to multiple vibes if applicable.
Return ONLY a JSON array of vibes, e.g. ["chill", "aesthetic"]
Do not include any other text, explanation, or formatting."""

    payload = {
        'model': 'openai/gpt-3.5-turbo',
        'messages': [
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.3,
        'max_tokens': 50
    }

    try:
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=10
        )

        if response.status_code != 200:
            print(f"OpenRouter API error for place categorization: {response.text}")
            return []

        result = response.json()
        llm_response = result['choices'][0]['message']['content'].strip()

        # Parse JSON array from response
        vibes = json.loads(llm_response)

        # Validate vibes are from our valid set
        valid_vibes = [v for v in vibes if v in VALID_VIBES]
        return valid_vibes

    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM response as JSON: {e}")
        return []
    except Exception as e:
        print(f"Error categorizing place with LLM: {e}")
        return []
