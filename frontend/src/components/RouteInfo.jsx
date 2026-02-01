/**
 * Route information display component
 */

const vibeEmojis = {
  chill: '🌿',
  date: '💕',
  chaos: '🍻',
  aesthetic: '📸'
}

const typeLabels = {
  bar: 'Bar',
  night_club: 'Night Club',
  casino: 'Casino',
  bowling_alley: 'Bowling',
  cafe: 'Cafe',
  restaurant: 'Restaurant',
  bakery: 'Bakery',
  spa: 'Spa',
  florist: 'Florist',
  park: 'Park',
  library: 'Library',
  book_store: 'Bookstore',
  cemetery: 'Cemetery',
  museum: 'Museum',
  art_gallery: 'Art Gallery',
  tourist_attraction: 'Attraction',
  church: 'Church',
  city_hall: 'City Hall',
  zoo: 'Zoo',
  aquarium: 'Aquarium',
  movie_theater: 'Cinema',
  shopping_mall: 'Mall',
  stadium: 'Stadium',
  amusement_park: 'Theme Park',
  university: 'University',
  // New Places API types
  cultural_landmark: 'Landmark',
  historical_landmark: 'Historic Site',
  plaza: 'Plaza',
  national_park: 'National Park',
  hiking_area: 'Hiking',
  garden: 'Garden',
  performing_arts_theater: 'Theater',
  concert_hall: 'Concert Hall',
  live_music_venue: 'Live Music',
  comedy_club: 'Comedy Club',
  wine_bar: 'Wine Bar',
  cocktail_bar: 'Cocktail Bar',
  pub: 'Pub',
  coffee_shop: 'Coffee Shop',
  tea_house: 'Tea House',
  ice_cream_shop: 'Ice Cream',
  brunch_restaurant: 'Brunch',
  fine_dining_restaurant: 'Fine Dining',
  italian_restaurant: 'Italian',
  french_restaurant: 'French',
  japanese_restaurant: 'Japanese',
  indian_restaurant: 'Indian',
  mexican_restaurant: 'Mexican',
  food_court: 'Food Court',
  observation_deck: 'Viewpoint',
  botanical_garden: 'Botanical Garden',
  memorial: 'Memorial',
  monument: 'Monument'
}

const formatType = (type) => {
  return typeLabels[type] || type?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) || 'Place'
}

const renderStars = (rating) => {
  if (!rating) return null
  const fullStars = Math.floor(rating)
  const hasHalf = rating % 1 >= 0.5
  return (
    <span className="place-rating" title={`${rating.toFixed(1)} stars`}>
      {'★'.repeat(fullStars)}
      {hasHalf && '½'}
      <span className="rating-value">{rating.toFixed(1)}</span>
    </span>
  )
}

export const RouteInfo = ({ routeData, isCircular }) => {
  if (!routeData) return null

  const allPlaces = routeData.waypoints || routeData.places || []

  // Filter out hotels, motels, airports (except 5-star world famous hotels)
  const filteredPlaces = allPlaces.filter(place => {
    const placeType = (place.type || place.google_type || '').toLowerCase()

    // Excluded types
    const excludedTypes = [
      'hotel', 'motel', 'lodging', 'airport',
      'transit_station', 'bus_station', 'train_station'
    ]

    // Check if it's an excluded type
    const isExcluded = excludedTypes.some(type => placeType.includes(type))

    // If it's a hotel, only include if it's 5-star (rating >= 4.5 and highly rated)
    if (placeType.includes('hotel') || placeType.includes('lodging')) {
      return (place.rating || 0) >= 4.5 && (place.user_ratings_total || 0) >= 500
    }

    // Exclude all other excluded types
    if (isExcluded) {
      return false
    }

    return true
  })

  // Limit to 1-5 places
  const places = filteredPlaces.slice(0, Math.min(5, Math.max(1, filteredPlaces.length)))

  // Function to export route to Google Maps
  const exportToGoogleMaps = () => {
    if (!routeData || !routeData.route || !routeData.route.coordinates) return

    const coords = routeData.route.coordinates
    if (coords.length < 2) return

    // Get start and end coordinates
    const start = coords[0] // [lng, lat]
    const end = coords[coords.length - 1] // [lng, lat]

    // Build Google Maps URL
    // Format: https://www.google.com/maps/dir/?api=1&origin=LAT,LNG&destination=LAT,LNG&waypoints=LAT,LNG|LAT,LNG&travelmode=walking
    let url = `https://www.google.com/maps/dir/?api=1`
    url += `&origin=${start[1]},${start[0]}`
    url += `&destination=${end[1]},${end[0]}`

    // Add waypoints if we have places with coordinates
    if (places.length > 0) {
      const waypoints = places
        .filter(p => p.latitude && p.longitude)
        .map(p => `${p.latitude},${p.longitude}`)
        .join('|')

      if (waypoints) {
        url += `&waypoints=${waypoints}`
      }
    }

    url += `&travelmode=walking`

    // Open in new tab/window (will open Google Maps app on mobile if available)
    window.open(url, '_blank')
  }

  return (
    <div className="route-info">
      <h3>Your {routeData.vibe} walk {routeData.config.emoji}</h3>

      <div className="route-stats">
        <div className="stat">
          <span className="stat-icon">📏</span>
          <span className="stat-value">{(routeData.route.distance / 1000).toFixed(2)} km</span>
        </div>
        <div className="stat">
          <span className="stat-icon">⏱️</span>
          <span className="stat-value">{routeData.route.duration} min</span>
        </div>
        <div className="stat">
          <span className="stat-icon">{isCircular ? '🔄' : '➡️'}</span>
          <span className="stat-value">{isCircular ? 'Circular' : 'One-way'}</span>
        </div>
      </div>

      <p className="route-description">{routeData.description}</p>

      <button
        className="export-button"
        onClick={exportToGoogleMaps}
        title="Open this route in Google Maps"
      >
        <span className="export-icon">📍</span>
        Open in Google Maps
      </button>

      <div className="places-section">
        <h4>Places that shaped your route ({places.length})</h4>
        <p className="places-subtitle">
          These spots match your <strong>{routeData.vibe}</strong> vibe
        </p>
        <div className="places-list">
          {places.map((place, index) => (
            <div key={place.place_id || index} className="place-card">
              <div className="place-header">
                <span className="place-name">{place.name}</span>
                <span className="place-distance">{Math.round(place.distance)}m</span>
              </div>
              <div className="place-details">
                <span className="place-type">{formatType(place.type || place.google_type)}</span>
                {renderStars(place.rating)}
              </div>
              {place.vibes && place.vibes.length > 0 && (
                <div className="place-vibes">
                  {place.vibes.map(vibe => (
                    <span
                      key={vibe}
                      className={`vibe-tag ${vibe === routeData.vibe ? 'vibe-tag-active' : ''}`}
                      title={`This place has ${vibe} vibes`}
                    >
                      {vibeEmojis[vibe]} {vibe}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
        {filteredPlaces.length > 5 && (
          <p className="places-more">+ {filteredPlaces.length - 5} more places considered</p>
        )}
      </div>

      {routeData.directions && routeData.directions.steps && (
        <details className="directions-panel">
          <summary>Turn-by-turn directions ({routeData.directions.steps.length} steps)</summary>
          <div className="directions-list">
            {routeData.directions.steps.map((step, index) => (
              <div key={index} className="direction-step">
                <span className="step-number">{index + 1}</span>
                <div className="step-content">
                  <div className="step-instruction" dangerouslySetInnerHTML={{ __html: step.instruction }} />
                  <div className="step-meta">
                    {step.distance}m · {step.duration} min
                  </div>
                </div>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  )
}
