/**
 * Popup notification for generated routes
 */
import { useEffect, useState } from 'react'

export const RoutePopup = ({ routeData, onClose }) => {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    if (routeData) {
      // Show popup when route is generated
      setIsVisible(true)

      // Auto-hide after 4 seconds
      const timer = setTimeout(() => {
        setIsVisible(false)
        if (onClose) onClose()
      }, 4000)

      return () => clearTimeout(timer)
    } else {
      setIsVisible(false)
    }
  }, [routeData, onClose])

  if (!isVisible || !routeData) return null

  const placesCount = (routeData.waypoints || routeData.places || []).length

  return (
    <div className="route-popup">
      <button className="popup-close" onClick={() => setIsVisible(false)}>
        ×
      </button>
      <div className="popup-icon">✨</div>
      <div className="popup-content">
        <h4>Things to do along the way!</h4>
        <p>{placesCount} interesting spot{placesCount !== 1 ? 's' : ''} on your route</p>
      </div>
    </div>
  )
}
