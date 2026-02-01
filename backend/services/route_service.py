"""Route optimization and calculation service"""
from config import VIBE_CONFIGS
from utils.geo_utils import calculate_distance, calculate_angle


def find_places_near_route(route_coordinates, all_places, max_distance=100):
    """
    Find places that are close to the actual route path.

    Args:
        route_coordinates: List of [lon, lat] coordinates forming the route
        all_places: List of all available places
        max_distance: Maximum distance in meters from route to consider a place "on path"

    Returns:
        List of places that are near the route, sorted by relevance
    """
    if not route_coordinates or not all_places:
        return []

    places_with_min_distance = []

    # For each place, find the minimum distance to any point on the route
    for place in all_places:
        place_lat = place.get('latitude')
        place_lon = place.get('longitude')

        if not place_lat or not place_lon:
            continue

        # Sample route points (every 10th point to reduce computation)
        sample_interval = max(1, len(route_coordinates) // 50)
        sampled_coords = route_coordinates[::sample_interval]

        # Find minimum distance to route
        min_dist = float('inf')
        closest_route_index = 0

        for i, coord in enumerate(sampled_coords):
            # coord is [lon, lat], we need (lat, lon) for calculate_distance
            dist = calculate_distance(place_lat, place_lon, coord[1], coord[0])
            if dist < min_dist:
                min_dist = dist
                closest_route_index = i * sample_interval

        # Only include places within max_distance of the route
        if min_dist <= max_distance:
            place_copy = place.copy()
            place_copy['distance_to_route'] = min_dist
            place_copy['route_position'] = closest_route_index / len(route_coordinates)  # 0 to 1
            places_with_min_distance.append(place_copy)

    # Sort by position along route (so places appear in order)
    places_with_min_distance.sort(key=lambda p: p['route_position'])

    return places_with_min_distance


def score_place_for_vibe(place, vibe):
    """
    Simple scoring: if place is in the vibe, score by rating only.
    All places in the vibe are treated equally (no vibe weighting).

    Args:
        place: Place dictionary with 'vibes' and 'rating' keys
        vibe: Target vibe string

    Returns:
        Score (float) - 0 if place doesn't belong to vibe
    """
    # Check if place belongs to this vibe
    place_vibes = place.get('vibes', [])
    if vibe not in place_vibes:
        return 0

    # Score purely by rating (all vibe members are equal)
    return (place.get('rating') or 3.0) * 10


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
    """Select optimal waypoints based on route type.

    Places should already be filtered to the requested vibe (from place_service).
    Scoring is based purely on rating since all places in the vibe are equal.
    """
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
        # Use 3 waypoints positioned at ~120 degree intervals to minimize overlap

        # Score places - use module-level score_place_for_vibe if vibes available,
        # otherwise fall back to rating-only scoring
        def local_score(place):
            # If place has vibes list (from place_service), use vibe-aware scoring
            if 'vibes' in place and place['vibes']:
                return score_place_for_vibe(place, vibe)
            # Fallback for legacy places without vibes
            return (place.get('rating') or 3.0) * 10

        # Score and sort places by rating (all in vibe are equal)
        scored_places = [(p, local_score(p)) for p in filtered_places]
        scored_places.sort(key=lambda x: x[1], reverse=True)

        # Try to select 3 waypoints at different angles for better loop coverage
        if len(scored_places) >= 3:
            selected_waypoints = []
            selected_angles = []

            # Select first waypoint from top candidates
            top_candidates = [p for p, score in scored_places[:5] if score > 50]
            if not top_candidates:
                top_candidates = [p for p, score in scored_places[:5]]

            vibe_index = hash(vibe) % len(top_candidates)
            waypoint1 = top_candidates[vibe_index]
            angle1 = calculate_angle(start_lat, start_lon, waypoint1['latitude'], waypoint1['longitude'])
            selected_waypoints.append(waypoint1)
            selected_angles.append(angle1)

            # Select second waypoint ~120 degrees away from first
            remaining = [p for p, s in scored_places if p != waypoint1 and s > 0]
            if remaining:
                # Find waypoint closest to 120 degrees from first
                target_angle_2 = (angle1 + 120) % 360
                waypoint2 = min(
                    remaining,
                    key=lambda p: min(
                        abs((calculate_angle(start_lat, start_lon, p['latitude'], p['longitude']) - target_angle_2 + 180) % 360 - 180),
                        360 - abs((calculate_angle(start_lat, start_lon, p['latitude'], p['longitude']) - target_angle_2 + 180) % 360 - 180)
                    )
                )
                angle2 = calculate_angle(start_lat, start_lon, waypoint2['latitude'], waypoint2['longitude'])
                selected_waypoints.append(waypoint2)
                selected_angles.append(angle2)

                # Select third waypoint ~120 degrees from second (240 degrees from first)
                remaining2 = [p for p in remaining if p != waypoint2]
                if remaining2:
                    target_angle_3 = (angle1 + 240) % 360
                    waypoint3 = min(
                        remaining2,
                        key=lambda p: min(
                            abs((calculate_angle(start_lat, start_lon, p['latitude'], p['longitude']) - target_angle_3 + 180) % 360 - 180),
                            360 - abs((calculate_angle(start_lat, start_lon, p['latitude'], p['longitude']) - target_angle_3 + 180) % 360 - 180)
                        )
                    )
                    selected_waypoints.append(waypoint3)

            # Create loop with 2-3 waypoints
            if len(selected_waypoints) >= 2:
                waypoints = [(start_lat, start_lon)]
                for wp in selected_waypoints:
                    waypoints.append((wp['latitude'], wp['longitude']))
                waypoints.append((start_lat, start_lon))
            else:
                # Fallback to simple route
                return create_simple_circular_route(start_lat, start_lon, target_distance)

        elif len(scored_places) >= 2:
            # Only 2 places available - ensure they're at different angles
            waypoint1 = scored_places[0][0]
            angle1 = calculate_angle(start_lat, start_lon, waypoint1['latitude'], waypoint1['longitude'])

            # Find second waypoint with maximum angle difference
            waypoint2 = max(
                [p for p, s in scored_places[1:] if s > 0],
                key=lambda p: abs((calculate_angle(start_lat, start_lon, p['latitude'], p['longitude']) - angle1 + 180) % 360 - 180),
                default=scored_places[1][0] if len(scored_places) > 1 else waypoint1
            )

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
        # One-way: select endpoint and waypoints based on rating
        # (places are already filtered to the requested vibe)

        # Score places - use rating-based scoring
        def local_score(place):
            # If place has vibes list (from place_service), use vibe-aware scoring
            if 'vibes' in place and place['vibes']:
                return score_place_for_vibe(place, vibe)
            # Fallback for legacy places without vibes
            return (place.get('rating') or 3.0) * 10

        # Score and sort places by rating
        scored_places = [(p, local_score(p)) for p in filtered_places]
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
