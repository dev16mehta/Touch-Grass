"""Configuration for vibe-based walking routes"""

# Valid vibes
VALID_VIBES = ['chill', 'date', 'chaos', 'aesthetic']

# Mapping from Google place types to vibes (binary: place is IN a vibe or NOT)
# Includes types for both legacy and new Places API
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

    # New Places API returns these additional types
    'cultural_landmark': ['aesthetic', 'chill'],
    'historical_landmark': ['aesthetic', 'chill'],
    'plaza': ['aesthetic', 'date', 'chill'],
    'national_park': ['chill', 'aesthetic', 'date'],
    'hiking_area': ['chill', 'aesthetic'],
    'garden': ['chill', 'aesthetic', 'date'],
    'performing_arts_theater': ['aesthetic', 'date'],
    'concert_hall': ['aesthetic', 'date', 'chaos'],
    'live_music_venue': ['chaos', 'date'],
    'comedy_club': ['chaos', 'date'],
    'karaoke': ['chaos'],
    'wine_bar': ['date', 'chill'],
    'cocktail_bar': ['date', 'chaos'],
    'pub': ['chaos', 'chill'],
    'coffee_shop': ['chill', 'date', 'aesthetic'],
    'tea_house': ['chill', 'date'],
    'ice_cream_shop': ['date', 'chill'],
    'dessert_shop': ['date', 'chill'],
    'brunch_restaurant': ['date', 'chill'],
    'fine_dining_restaurant': ['date'],
    'italian_restaurant': ['date'],
    'french_restaurant': ['date'],
    'japanese_restaurant': ['date'],
    'indian_restaurant': ['date'],
    'mexican_restaurant': ['chaos', 'date'],
    'food_court': ['chaos'],
    'fast_food_restaurant': ['chaos'],
    'observation_deck': ['aesthetic', 'date'],
    'botanical_garden': ['chill', 'aesthetic', 'date'],
    'sculpture': ['aesthetic'],
    'monument': ['aesthetic'],
    'memorial': ['aesthetic', 'chill'],
}

# Types to search for with the Places API (New)
# Only includes types that are valid for the includedTypes parameter
# Reference: https://developers.google.com/maps/documentation/places/web-service/place-types
ALL_DISCOVERABLE_TYPES = [
    # Core types that work with Places API (New)
    'bar', 'night_club', 'casino', 'bowling_alley', 'stadium', 'amusement_park',
    'shopping_mall', 'cafe', 'restaurant', 'bakery', 'spa', 'florist',
    'movie_theater', 'park', 'library', 'book_store', 'museum', 'art_gallery',
    'tourist_attraction', 'church', 'city_hall', 'aquarium', 'zoo', 'university',
    'national_park', 'hiking_area', 'performing_arts_theater', 'coffee_shop',
]

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
