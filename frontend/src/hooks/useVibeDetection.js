/**
 * Hook for detecting vibe from mood text
 */
import { useState } from 'react'
import { detectVibe as detectVibeAPI } from '../services/api'

export const useVibeDetection = () => {
  const [moodText, setMoodText] = useState('')
  const [detectedVibe, setDetectedVibe] = useState(null)
  const [detecting, setDetecting] = useState(false)
  const [error, setError] = useState(null)

  const detectVibe = async () => {
    if (!moodText.trim()) {
      setError('Please describe how you feel')
      return
    }

    setDetecting(true)
    setError(null)

    try {
      const result = await detectVibeAPI(moodText)
      setDetectedVibe(result)
      return result.vibe
    } catch (err) {
      console.error('Error detecting vibe:', err)
      setError(err.response?.data?.error || 'Failed to detect vibe')
      return null
    } finally {
      setDetecting(false)
    }
  }

  return {
    moodText,
    setMoodText,
    detectedVibe,
    detecting,
    detectVibe,
    error
  }
}
