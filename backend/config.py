"""Configuration for vibe-based walking routes"""

VIBE_CONFIGS = {
    'chill': {
        'emoji': '🌿',
        'description': 'Relaxing walk with parks and quiet spots',
        'place_types': ['park', 'cafe', 'garden'],
        'pace': 'moderate',
        'pace_multiplier': 1.0,
        'google_types': ['park', 'cafe', 'natural_feature'],
        'noise_preference': 'quiet'
    },
    'date': {
        'emoji': '💕',
        'description': 'Romantic walk with cafes and scenic views',
        'place_types': ['cafe', 'restaurant', 'park', 'viewpoint'],
        'pace': 'moderate',
        'pace_multiplier': 1.0,
        'google_types': ['cafe', 'restaurant', 'park', 'bakery'],
        'noise_preference': 'moderate'
    },
    'chaos': {
        'emoji': '🍻',
        'description': 'Energetic walk with bars and nightlife',
        'place_types': ['bar', 'pub', 'restaurant', 'entertainment'],
        'pace': 'moderate',
        'pace_multiplier': 1.0,
        'google_types': ['bar', 'night_club', 'restaurant'],
        'noise_preference': 'lively'
    },
    'aesthetic': {
        'emoji': '📸',
        'description': 'Instagram-worthy spots and scenic views',
        'place_types': ['viewpoint', 'park', 'landmark', 'cafe'],
        'pace': 'moderate',
        'pace_multiplier': 1.0,
        'google_types': ['tourist_attraction', 'park', 'art_gallery', 'museum'],
        'noise_preference': 'any'
    }
}
