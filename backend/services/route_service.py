"""Route optimization and calculation service"""
from config import VIBE_CONFIGS
from utils.geo_utils import calculate_distance, calculate_angle


def calculate_route_parameters(duration_minutes, vibe, is_circular):
    """Calculate target distance and search radius based on duration"""
    vibe_config = VIBE_CONFIGS[vibe]
    base_speed_m_per_min = 80  # 5 km/h = 80 m/min
    pace_multiplier = vibe_config.get('pace_multiplier', 1.0)

    actual_speed = base_speed_m_per_min * pace_multiplier
    target_distance = duration_minutes * actual_speed

    # Reduced search radius to find POIs closer to start
    # Accounts for routing overhead (streets are ~1.4x straight-line)
    if is_circular:
        search_radius = target_distance / 4  # Conservative for circular routes
    else:
        search_radius = target_distance / 3  # Conservative for one-way routes

    return {
        'target_distance': target_distance,
        'search_radius': min(search_radius, 5000),  # Cap at 5km for more accurate routes
        'expected_duration': duration_minutes
    }


def optimize_waypoints(start_lat, start_lon, places, target_distance, vibe, is_circular):
    """Select optimal waypoints based on route type"""
    if not places:
        return create_simple_circular_route(start_lat, start_lon, target_distance)

    # Use 2 waypoints for circular (to create a loop), 2 for one-way
    num_waypoints = 2

    # Filter places to only those within reasonable distance
    # Account for routing overhead (streets are ~1.4x straight-line distance)
    # For circular loop with 2 waypoints: ~3 segments * 1.4x = 4.2x total
    # So max_distance = target_distance / 4.5
    # For one-way: max distance should be target_distance/4
    max_distance = (target_distance / 4.5) if is_circular else (target_distance / 4)

    # Filter places by distance
    filtered_places = [
        p for p in places
        if calculate_distance(start_lat, start_lon, p['latitude'], p['longitude']) <= max_distance
    ]

    # If no places within range, use the closest ones
    if not filtered_places:
        filtered_places = sorted(
            places,
            key=lambda p: calculate_distance(start_lat, start_lon, p['latitude'], p['longitude'])
        )[:num_waypoints * 2]

    if is_circular:
        # For circular routes, create a LOOP (not out-and-back)
        # Select 2 waypoints at different angles to create a triangular loop
        vibe_config = VIBE_CONFIGS.get(vibe, {})
        preferred_types = vibe_config.get('google_types', [])

        # Score places based on vibe match - prefer primary vibe types
        def score_place_for_vibe(place):
            place_type = place['type']
            # Primary types get highest score (100)
            if preferred_types and place_type == preferred_types[0]:
                return 100 + place['rating'] * 10
            # Secondary types get medium score (50)
            elif place_type in preferred_types:
                return 50 + place['rating'] * 10
            # Other types get low score
            else:
                return place['rating'] * 10

        # Score and sort places by vibe preference
        scored_places = [(p, score_place_for_vibe(p)) for p in filtered_places]
        scored_places.sort(key=lambda x: x[1], reverse=True)

        if len(scored_places) >= 2:
            # Select first waypoint from top 3 vibe-matching places (adds variety)
            top_candidates = [p for p, score in scored_places[:3] if score > 50]
            if not top_candidates:
                top_candidates = [p for p, score in scored_places[:3]]

            # Use hash of vibe to get consistent but different selection per vibe
            vibe_index = hash(vibe) % len(top_candidates)
            waypoint1 = top_candidates[vibe_index]

            # Second waypoint: pick one at different angle that also matches vibe
            angle_to_wp1 = calculate_angle(start_lat, start_lon, waypoint1['latitude'], waypoint1['longitude'])

            # Get remaining high-scoring places
            remaining = [(p, s) for p, s in scored_places if p != waypoint1]

            if remaining:
                # Prefer places that: 1) match vibe well, 2) are at different angle
                waypoint2 = max(
                    remaining,
                    key=lambda x: (
                        x[1] * 0.5 +  # Vibe score weight
                        abs((calculate_angle(start_lat, start_lon, x[0]['latitude'], x[0]['longitude']) - angle_to_wp1 + 180) % 360 - 180) * 0.5  # Angle difference weight
                    )
                )[0]
            else:
                waypoint2 = scored_places[1][0] if len(scored_places) > 1 else waypoint1

            # Create loop: Start → WP1 → WP2 → Start
            waypoints = [
                (start_lat, start_lon),
                (waypoint1['latitude'], waypoint1['longitude']),
                (waypoint2['latitude'], waypoint2['longitude']),
                (start_lat, start_lon)
            ]
        elif scored_places:
            # Only 1 place available - create simple out-and-back
            waypoint = scored_places[0][0]
            waypoints = [
                (start_lat, start_lon),
                (waypoint['latitude'], waypoint['longitude']),
                (start_lat, start_lon)
            ]
        else:
            # No places - use fallback
            return create_simple_circular_route(start_lat, start_lon, target_distance)

    else:
        # One-way: select endpoint and waypoints based on vibe preferences
        vibe_config = VIBE_CONFIGS.get(vibe, {})
        preferred_types = vibe_config.get('google_types', [])

        # Score places based on vibe match
        def score_place_for_vibe(place):
            place_type = place['type']
            # Primary types get highest score (100)
            if preferred_types and place_type == preferred_types[0]:
                return 100 + place['rating'] * 10
            # Secondary types get medium score (50)
            elif place_type in preferred_types:
                return 50 + place['rating'] * 10
            # Other types get low score
            else:
                return place['rating'] * 10

        # Score and sort places by vibe preference
        scored_places = [(p, score_place_for_vibe(p)) for p in filtered_places]
        scored_places.sort(key=lambda x: x[1], reverse=True)

        # Endpoint should be ~20% of target distance
        target_endpoint_dist = target_distance * 0.2

        # Find endpoint from high-scoring places
        if scored_places:
            # Select from top vibe-matching places
            top_candidates = [p for p, score in scored_places if score > 50]
            if not top_candidates:
                top_candidates = [p for p, _ in scored_places]

            # Use vibe hash for consistent variety
            vibe_index = hash(vibe) % min(3, len(top_candidates))
            endpoint_candidates = top_candidates[:3] if len(top_candidates) >= 3 else top_candidates

            # Pick endpoint close to target distance
            endpoint = min(
                endpoint_candidates,
                key=lambda p: abs(
                    calculate_distance(start_lat, start_lon, p['latitude'], p['longitude'])
                    - target_endpoint_dist
                )
            )

            # Remove endpoint from scored places
            remaining_places = [(p, s) for p, s in scored_places if p != endpoint]
        else:
            # Use farthest place within max_distance
            endpoint = max(
                [p for p in places if calculate_distance(start_lat, start_lon, p['latitude'], p['longitude']) <= max_distance],
                key=lambda p: calculate_distance(start_lat, start_lon, p['latitude'], p['longitude']),
                default=places[0] if places else None
            )
            remaining_places = []

        # Select 1 intermediate waypoint between start and endpoint
        intermediates = []
        if remaining_places and endpoint:
            # Find high-scoring place roughly halfway
            mid_lat = (start_lat + endpoint['latitude']) / 2
            mid_lon = (start_lon + endpoint['longitude']) / 2

            nearest = min(
                remaining_places,
                key=lambda x: calculate_distance(
                    mid_lat, mid_lon, x[0]['latitude'], x[0]['longitude']
                )
            )[0]
            intermediates.append(nearest)

        if endpoint:
            waypoints = [(start_lat, start_lon)] + [
                (p['latitude'], p['longitude']) for p in intermediates
            ] + [(endpoint['latitude'], endpoint['longitude'])]
        else:
            # Fallback to simple route
            waypoints = [(start_lat, start_lon), (start_lat + 0.001, start_lon + 0.001)]

    return waypoints


def create_simple_circular_route(lat, lon, target_distance):
    """Create a simple circular route when no POIs available"""
    # Account for routing overhead: actual routes are ~1.4x straight-line
    # For circular loop with 2 waypoints: divide by 6
    radius_degrees = (target_distance / 6) / 111320  # Convert meters to degrees

    # Create triangular loop: Start → East → North → Start
    waypoints = [
        (lat, lon),  # Start
        (lat, lon + radius_degrees),  # East
        (lat + radius_degrees, lon),  # North
        (lat, lon)  # Back to start
    ]
    return waypoints
