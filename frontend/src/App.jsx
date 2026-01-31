import { useState, useEffect, useRef } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import axios from 'axios'
import './App.css'

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN

// Validate and set API URL
const getApiUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL
  if (envUrl) {
    // Ensure it has protocol and host
    if (envUrl.startsWith('http://') || envUrl.startsWith('https://')) {
      return envUrl
    }
    // If it starts with :, it's likely malformed
    if (envUrl.startsWith(':')) {
      console.warn('Invalid VITE_API_URL format. Using default.')
      return 'http://localhost:5001/api'
    }
    return envUrl
  }
  return 'http://localhost:5001/api'
}

const API_URL = getApiUrl()

function App() {
  const [vibes, setVibes] = useState([])
  const [selectedVibe, setSelectedVibe] = useState('chill')
  const [location, setLocation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [routeData, setRouteData] = useState(null)
  const [error, setError] = useState(null)

  const mapContainer = useRef(null)
  const map = useRef(null)

  // Fetch available vibes
  useEffect(() => {
    fetchVibes()
    getCurrentLocation()
  }, [])

  // Initialize map
  useEffect(() => {
    if (map.current || !location) return

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [location.longitude, location.latitude],
      zoom: 13
    })

    // Add user location marker
    new mapboxgl.Marker({ color: '#FF0000' })
      .setLngLat([location.longitude, location.latitude])
      .setPopup(new mapboxgl.Popup().setHTML("<h3>You are here</h3>"))
      .addTo(map.current)

  }, [location])

  // Update route on map
  useEffect(() => {
    if (!routeData || !map.current) return

    // Clear existing layers and sources
    if (map.current.getLayer('route')) {
      map.current.removeLayer('route')
    }
    if (map.current.getSource('route')) {
      map.current.removeSource('route')
    }

    // Remove existing markers (except user location)
    const markers = document.querySelectorAll('.mapboxgl-marker:not([style*="rgb(255, 0, 0)"])')
    markers.forEach(marker => marker.remove())

    // Add route line
    const coordinates = routeData.route

    map.current.addSource('route', {
      type: 'geojson',
      data: {
        type: 'Feature',
        properties: {},
        geometry: {
          type: 'LineString',
          coordinates: coordinates
        }
      }
    })

    map.current.addLayer({
      id: 'route',
      type: 'line',
      source: 'route',
      layout: {
        'line-join': 'round',
        'line-cap': 'round'
      },
      paint: {
        'line-color': getVibeColor(selectedVibe),
        'line-width': 4,
        'line-opacity': 0.8
      }
    })

    // Add place markers
    routeData.places.forEach((place, index) => {
      const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(
        `<h3>${place.name}</h3><p>${place.type}</p><p>${Math.round(place.distance)}m away</p>`
      )

      new mapboxgl.Marker({ color: getVibeColor(selectedVibe) })
        .setLngLat([place.longitude, place.latitude])
        .setPopup(popup)
        .addTo(map.current)
    })

    // Fit map to route bounds
    const bounds = new mapboxgl.LngLatBounds()
    coordinates.forEach(coord => bounds.extend(coord))
    map.current.fitBounds(bounds, { padding: 50 })

  }, [routeData, selectedVibe])

  const fetchVibes = async () => {
    try {
      const response = await axios.get(`${API_URL}/vibes`)
      setVibes(response.data.vibes)
      setError(null) // Clear any previous errors
    } catch (err) {
      console.error('Error fetching vibes:', err)
      // Provide fallback vibes if API is unavailable
      const fallbackVibes = [
        { id: 'chill', name: 'Chill', emoji: '🌿' },
        { id: 'date', name: 'Date', emoji: '💕' },
        { id: 'chaos', name: 'Chaos', emoji: '🍻' },
        { id: 'aesthetic', name: 'Aesthetic', emoji: '📸' }
      ]
      setVibes(fallbackVibes)
      setError('Backend server not running. Using fallback vibes. Please start the backend server at http://localhost:5001')
    }
  }

  const getCurrentLocation = () => {
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
  }

  const generateRoute = async () => {
    if (!location) {
      setError('Location not available')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_URL}/generate-route`, {
        vibe: selectedVibe,
        latitude: location.latitude,
        longitude: location.longitude,
        radius: 2000
      })

      setRouteData(response.data)
    } catch (err) {
      console.error('Error generating route:', err)
      setError(err.response?.data?.error || 'Failed to generate route')
    } finally {
      setLoading(false)
    }
  }

  const getVibeColor = (vibe) => {
    const colors = {
      chill: '#10b981',
      date: '#ec4899',
      chaos: '#f59e0b',
      aesthetic: '#8b5cf6'
    }
    return colors[vibe] || '#3b82f6'
  }

  return (
    <div className="app">
      <div className="sidebar">
        <div className="header">
          <h1>🌿 Touch Grass</h1>
          <p className="tagline">Mood-Based Walking Routes</p>
        </div>

        <div className="vibe-selector">
          <h2>Pick Your Vibe</h2>
          <div className="vibe-grid">
            {vibes.map((vibe) => (
              <button
                key={vibe.id}
                className={`vibe-button ${selectedVibe === vibe.id ? 'active' : ''}`}
                onClick={() => setSelectedVibe(vibe.id)}
                style={{
                  borderColor: selectedVibe === vibe.id ? getVibeColor(vibe.id) : '#e5e7eb'
                }}
              >
                <span className="vibe-emoji">{vibe.emoji}</span>
                <span className="vibe-name">{vibe.name}</span>
              </button>
            ))}
          </div>
        </div>

        <button
          className="generate-button"
          onClick={generateRoute}
          disabled={loading || !location}
          style={{ backgroundColor: getVibeColor(selectedVibe) }}
        >
          {loading ? 'Generating...' : '✨ Generate Route'}
        </button>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {routeData && (
          <div className="route-info">
            <h3>Your {routeData.vibe} walk {routeData.config.emoji}</h3>
            <p className="route-description">{routeData.description}</p>

            <div className="places-list">
              <h4>Places on your route:</h4>
              {routeData.places.slice(0, 5).map((place, index) => (
                <div key={index} className="place-item">
                  <span className="place-name">{place.name}</span>
                  <span className="place-distance">{Math.round(place.distance)}m</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="map-container">
        <div ref={mapContainer} className="map" />
      </div>
    </div>
  )
}

export default App
