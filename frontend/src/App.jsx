/**
 * Main App component for Touch Grass
 */
import { useState } from 'react'
import 'mapbox-gl/dist/mapbox-gl.css'
import './App.css'
import { Leaf, Sprout } from 'lucide-react'

import { Map, MoodSelector, DurationSelector, RouteTypeSelector, DestinationSelector, RouteInfo, PlacesPopup } from './components'
import { useLocation, useVibeDetection, useRouteGeneration } from './hooks'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api'

const getVibeColor = (vibe) => {
  const colors = {
    chill: '#10b981',
    date: '#ec4899',
    chaos: '#f59e0b',
    aesthetic: '#8b5cf6'
  }
  return colors[vibe] || '#3b82f6'
}

function App() {
  const [selectedVibe, setSelectedVibe] = useState('chill')
  const [duration, setDuration] = useState('')
  const [isCircular, setIsCircular] = useState(true)
  const [destination, setDestination] = useState('')
  const [geocodedDestination, setGeocodedDestination] = useState(null)
  const [geocoding, setGeocoding] = useState(false)

  // Custom hooks
  const { location: gpsLocation, error: locationError } = useLocation()
  const {
    moodText,
    setMoodText,
    detectedVibe,
    detectedLocation,
    detecting,
    detectVibe,
    clearDetectedLocation,
    error: vibeError
  } = useVibeDetection()
  const {
    loading,
    routeData,
    error: routeError,
    generateRoute: generateRouteAPI,
    setError: setRouteError
  } = useRouteGeneration()

  // Use detected location if available, otherwise use GPS location
  const activeLocation = detectedLocation || gpsLocation

  // Combined error
  const error = locationError || vibeError || routeError

  const handleDetectVibe = async () => {
    const result = await detectVibe()
    if (result.vibe) {
      setSelectedVibe(result.vibe)
    }
  }

  const handleClearLocation = () => {
    clearDetectedLocation()
  }

  const handleGeocodeDestination = async (destText) => {
    setGeocoding(true)
    try {
      const response = await axios.post(`${API_URL}/geocode`, {
        location: destText
      })
      if (response.data.geocoded_location) {
        setGeocodedDestination(response.data.geocoded_location)
      }
    } catch (err) {
      console.error('Failed to geocode destination:', err)
      setRouteError('Could not find destination. Please try a different address.')
    } finally {
      setGeocoding(false)
    }
  }

  const handleClearDestination = () => {
    setDestination('')
    setGeocodedDestination(null)
  }

  const handleGenerateRoute = async () => {
    if (!activeLocation) {
      setRouteError('Location not available')
      return
    }

    // For one-way routes, require a destination
    if (!isCircular && !geocodedDestination) {
      setRouteError('Please enter a destination for your one-way route')
      return
    }

    // Auto-detect vibe if user hasn't detected it yet but has entered text
    if (moodText.trim() && !detectedVibe) {
      const result = await detectVibe()
      if (result.vibe) {
        setSelectedVibe(result.vibe)
      }
      // Let user click generate again after vibe is detected
      return
    }

    await generateRouteAPI({
      vibe: selectedVibe,
      location: activeLocation,
      destination: geocodedDestination,
      duration,
      isCircular
    })
  }

  return (
    <div className="app">
      <div className="sidebar">
        <div className="header">
          <h1><Leaf className="header-icon" /> Touch Grass</h1>
          <p className="tagline">Mood-Based Walking Routes</p>
        </div>

        <MoodSelector
          moodText={moodText}
          onMoodTextChange={setMoodText}
          onDetect={handleDetectVibe}
          detecting={detecting}
          detectedVibe={detectedVibe}
          detectedLocation={detectedLocation}
          onClearLocation={handleClearLocation}
        />

        <DurationSelector
          duration={duration}
          onDurationChange={setDuration}
        />

        <RouteTypeSelector
          isCircular={isCircular}
          onToggle={setIsCircular}
        />

        {!isCircular && (
          <DestinationSelector
            destination={destination}
            onDestinationChange={setDestination}
            onGeocode={handleGeocodeDestination}
            geocoding={geocoding}
            geocodedDest={geocodedDestination}
            onClearDest={handleClearDestination}
          />
        )}

        <button
          className="generate-button"
          onClick={handleGenerateRoute}
          disabled={loading || !activeLocation || !duration}
          style={{ backgroundColor: getVibeColor(selectedVibe) }}
        >
          {loading ? (
            <>
              <Sprout className="button-icon growing" />
              Growing your path...
            </>
          ) : (
            <>
              <Leaf className="button-icon" />
              Start Exploring
            </>
          )}
        </button>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <RouteInfo
          routeData={routeData}
          isCircular={isCircular}
        />
      </div>

      <div className="map-container">
        <Map
          location={activeLocation}
          routeData={routeData}
          selectedVibe={selectedVibe}
        />
        <PlacesPopup routeData={routeData} />
      </div>
    </div>
  )
}

export default App
