/**
 * Hook for generating walking routes
 */
import { useState } from 'react'
import { generateRoute as generateRouteAPI } from '../services/api'

export const useRouteGeneration = () => {
  const [loading, setLoading] = useState(false)
  const [routeData, setRouteData] = useState(null)
  const [error, setError] = useState(null)

  const generateRoute = async ({ vibe, location, duration, isCircular }) => {
    if (!location) {
      setError('Location not available')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const result = await generateRouteAPI({
        vibe,
        latitude: location.latitude,
        longitude: location.longitude,
        duration,
        circular: isCircular
      })
      setRouteData(result)
      return result
    } catch (err) {
      console.error('Error generating route:', err)
      setError(err.response?.data?.error || 'Failed to generate route')
      return null
    } finally {
      setLoading(false)
    }
  }

  return {
    loading,
    routeData,
    error,
    generateRoute,
    setError
  }
}
