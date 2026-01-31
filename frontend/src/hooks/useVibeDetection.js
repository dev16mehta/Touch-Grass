/**
 * Hook for detecting vibe and location from mood text
 */
import { useState } from 'react'
import { detectVibe as detectVibeAPI } from '../services/api'

export const useVibeDetection = () => {
  const [moodText, setMoodText] = useState('')
  const [detectedVibe, setDetectedVibe] = useState(null)
  const [detectedLocation, setDetectedLocation] = useState(null)
  const [detecting, setDetecting] = useState(false)
  const [error, setError] = useState(null)

  const detectVibe = async () => {
    if (!moodText.trim()) {
      setError('Please describe how you feel')
      return { vibe: null, location: null }
    }

    setDetecting(true)
    setError(null)

    try {
      const result = await detectVibeAPI(moodText)
      setDetectedVibe(result)

      // Handle location
      if (result.geocoded_location) {
        setDetectedLocation(result.geocoded_location)
      } else if (result.location_error) {
        setError(result.location_error)
      }

      return {
        vibe: result.vibe,
        location: result.geocoded_location || null
      }
    } catch (err) {
      console.error('Error detecting vibe:', err)
      setError(err.response?.data?.error || 'Failed to detect vibe')
      return { vibe: null, location: null }
    } finally {
      setDetecting(false)
    }
  }

  const clearDetectedLocation = () => {
    setDetectedLocation(null)
  }

  return {
    moodText,
    setMoodText,
    detectedVibe,
    detectedLocation,
    detecting,
    detectVibe,
    clearDetectedLocation,
    error
  }
}
