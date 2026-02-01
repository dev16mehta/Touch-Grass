/**
 * API service for Touch Grass backend
 */
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api'

/**
 * Detect vibe from user's mood text
 */
export const detectVibe = async (moodText) => {
  const response = await axios.post(`${API_URL}/detect-vibe`, {
    text: moodText
  })
  return response.data
}

/**
 * Generate walking route based on parameters
 */
export const generateRoute = async ({ vibe, latitude, longitude, destination, duration, circular }) => {
  const response = await axios.post(`${API_URL}/generate-route`, {
    vibe,
    latitude,
    longitude,
    destination,
    duration,
    circular
  })
  return response.data
}

/**
 * Health check
 */
export const healthCheck = async () => {
  const response = await axios.get(`${API_URL}/health`)
  return response.data
}
