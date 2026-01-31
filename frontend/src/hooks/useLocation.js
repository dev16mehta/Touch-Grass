/**
 * Hook for managing user location
 */
import { useState, useEffect } from 'react'

export const useLocation = () => {
  const [location, setLocation] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          })
        },
        (error) => {
          console.error('Error getting location:', error)
          // Default to San Francisco
          setLocation({ latitude: 37.7749, longitude: -122.4194 })
          setError('Could not get your location. Using default location.')
        }
      )
    } else {
      setLocation({ latitude: 37.7749, longitude: -122.4194 })
      setError('Geolocation not supported. Using default location.')
    }
  }, [])

  return { location, error }
}
