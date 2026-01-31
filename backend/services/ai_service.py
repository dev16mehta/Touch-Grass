"""AI service for LLM integrations (OpenRouter and Gemini)"""
import requests
from config import VIBE_CONFIGS


def detect_vibe_from_text(openrouter_api_key, user_text):
    """Detect vibe from user's text description using OpenRouter LLM"""
    if not openrouter_api_key:
        raise ValueError('OpenRouter API not configured')

    headers = {
        'Authorization': f'Bearer {openrouter_api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'http://localhost:5001',
        'X-Title': 'Touch Grass'
    }

    prompt = f"""You are a mood classifier for a walking route app. Based on the user's description, classify their mood into ONE of these vibes:

1. "chill" - Relaxing, peaceful, quiet, wanting to unwind, destress, calm, meditative
2. "date" - Romantic, with partner, coffee date, scenic, intimate, quality time
3. "chaos" - Party, energetic, nightlife, bars, adventure, wild, exciting
4. "aesthetic" - Photography, Instagram, beautiful views, artistic, scenic spots, pictures

User says: "{user_text}"

Respond with ONLY the vibe name (chill, date, chaos, or aesthetic). Nothing else."""

    payload = {
        'model': 'openai/gpt-3.5-turbo',
        'messages': [
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.3,
        'max_tokens': 10
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
    detected_vibe = result['choices'][0]['message']['content'].strip().lower()

    # Validate the detected vibe
    if detected_vibe not in VIBE_CONFIGS:
        # Default to chill if invalid
        detected_vibe = 'chill'

    return {
        'vibe': detected_vibe,
        'emoji': VIBE_CONFIGS[detected_vibe]['emoji'],
        'description': VIBE_CONFIGS[detected_vibe]['description']
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
