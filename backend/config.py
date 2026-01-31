"""Configuration for vibe-based walking routes"""

# Valid vibes
VALID_VIBES = ['chill', 'date', 'chaos', 'aesthetic']

# Mapping from Google place types to vibes (binary: place is IN a vibe or NOT)
# Only includes valid Google Places API types for places_nearby()
PLACE_TYPE_TO_VIBES = {
    # Chaos (nightlife, energetic)
    'bar': ['chaos'],
    'night_club': ['chaos'],
    'casino': ['chaos'],
    'bowling_alley': ['chaos', 'date'],
    'stadium': ['chaos', 'aesthetic'],
    'amusement_park': ['chaos', 'date'],
    'shopping_mall': ['chaos', 'date'],
    'liquor_store': ['chaos'],

    # Date (romantic, intimate)
    'cafe': ['date', 'chill', 'aesthetic'],
    'restaurant': ['date'],
    'bakery': ['date', 'chill'],
    'spa': ['date', 'chill'],
    'florist': ['date', 'aesthetic'],
    'movie_theater': ['date'],

    # Chill (peaceful, nature)
    'park': ['chill', 'date', 'aesthetic'],
    'library': ['chill'],
    'book_store': ['chill'],
    'cemetery': ['chill', 'aesthetic'],
    'campground': ['chill'],
    'rv_park': ['chill'],

    # Aesthetic (photogenic, cultural)
    'museum': ['aesthetic', 'date', 'chill'],
    'art_gallery': ['aesthetic', 'date'],
    'tourist_attraction': ['aesthetic', 'date'],
    'church': ['aesthetic', 'chill'],
    'city_hall': ['aesthetic'],
    'courthouse': ['aesthetic'],
    'embassy': ['aesthetic'],
    'hindu_temple': ['aesthetic', 'chill'],
    'mosque': ['aesthetic', 'chill'],
    'synagogue': ['aesthetic', 'chill'],
    'aquarium': ['aesthetic', 'date', 'chill'],
    'zoo': ['aesthetic', 'date', 'chill'],
    'university': ['aesthetic', 'chill'],
}

# All types we'll try to fetch from Google Places API
# These are valid type parameters for places_nearby()
ALL_DISCOVERABLE_TYPES = list(PLACE_TYPE_TO_VIBES.keys())

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
