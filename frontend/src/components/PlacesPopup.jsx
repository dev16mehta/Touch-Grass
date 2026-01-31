/**
 * Popup that shows when a route is generated with places count
 */
import { useEffect, useState } from 'react'

export const PlacesPopup = ({ routeData }) => {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    if (routeData) {
      // Show popup when route is generated
      setIsVisible(true)

      // Auto-hide after 5 seconds
      const timer = setTimeout(() => {
        setIsVisible(false)
      }, 5000)

      return () => clearTimeout(timer)
    } else {
      setIsVisible(false)
    }
  }, [routeData])

  if (!isVisible || !routeData) return null

  // Count places (same filtering logic as RouteInfo)
  const allPlaces = routeData.waypoints || routeData.places || []

  const filteredPlaces = allPlaces.filter(place => {
    const placeType = (place.type || place.google_type || '').toLowerCase()

    const excludedTypes = [
      'hotel', 'motel', 'lodging', 'airport',
      'transit_station', 'bus_station', 'train_station'
    ]

    const isExcluded = excludedTypes.some(type => placeType.includes(type))

    if (placeType.includes('hotel') || placeType.includes('lodging')) {
      return (place.rating || 0) >= 4.5 && (place.user_ratings_total || 0) >= 500
    }

    if (isExcluded) {
      return false
    }

    return true
  })

  const placesCount = Math.min(5, Math.max(1, filteredPlaces.length))

  return (
    <div className="places-popup">
      <button
        className="popup-close"
        onClick={() => setIsVisible(false)}
        aria-label="Close"
      >
        ×
      </button>
      <div className="popup-icon">🎯</div>
      <div className="popup-content">
        <h4>Places of interest found</h4>
        <p className="popup-count">{placesCount}</p>
      </div>
    </div>
  )
}
