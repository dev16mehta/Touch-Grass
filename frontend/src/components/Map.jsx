/**
 * Mapbox map component for displaying routes
 */
import { useEffect, useRef } from 'react'
import mapboxgl from 'mapbox-gl'

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN

const getVibeColor = (vibe) => {
  const colors = {
    chill: '#10b981',
    date: '#ec4899',
    chaos: '#f59e0b',
    aesthetic: '#8b5cf6'
  }
  return colors[vibe] || '#3b82f6'
}

export const Map = ({ location, routeData, selectedVibe }) => {
  const mapContainer = useRef(null)
  const map = useRef(null)

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
    if (map.current.getLayer('route-arrows')) {
      map.current.removeLayer('route-arrows')
    }
    if (map.current.getLayer('route')) {
      map.current.removeLayer('route')
    }
    if (map.current.getLayer('route-outline')) {
      map.current.removeLayer('route-outline')
    }
    if (map.current.getSource('route')) {
      map.current.removeSource('route')
    }

    // Remove existing markers (except user location red marker)
    const markers = document.querySelectorAll('.mapboxgl-marker:not([style*="rgb(255, 0, 0)"])')
    markers.forEach(marker => marker.remove())
    // Also remove start markers
    document.querySelectorAll('.start-marker').forEach(el => el.closest('.mapboxgl-marker')?.remove())

    // Add route line
    const coordinates = routeData.route.coordinates || routeData.route

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

    // Add shadow/outline layer first (bottom layer)
    map.current.addLayer({
      id: 'route-outline',
      type: 'line',
      source: 'route',
      layout: {
        'line-join': 'round',
        'line-cap': 'round'
      },
      paint: {
        'line-color': '#000000',
        'line-width': 10,
        'line-opacity': 0.3,
        'line-blur': 4
      }
    })

    // Add main route layer on top
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
        'line-width': 6,
        'line-opacity': 0.95
      }
    })

    // Add directional arrows along the route
    map.current.addLayer({
      id: 'route-arrows',
      type: 'symbol',
      source: 'route',
      layout: {
        'symbol-placement': 'line',
        'symbol-spacing': 50,
        'text-field': '▶',
        'text-size': 16,
        'text-keep-upright': false,
        'text-rotation-alignment': 'map'
      },
      paint: {
        'text-color': getVibeColor(selectedVibe),
        'text-halo-color': '#ffffff',
        'text-halo-width': 2
      }
    })

    // Add place markers
    const places = routeData.waypoints || routeData.places || []
    places.forEach((place) => {
      const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(
        `<h3>${place.name}</h3><p>${place.type}</p><p>${Math.round(place.distance)}m away</p>`
      )

      new mapboxgl.Marker({ color: getVibeColor(selectedVibe) })
        .setLngLat([place.longitude, place.latitude])
        .setPopup(popup)
        .addTo(map.current)
    })

    // Add starting point marker
    if (coordinates.length > 0) {
      const startEl = document.createElement('div')
      startEl.className = 'start-marker'
      startEl.innerHTML = `
        <div style="
          background: ${getVibeColor(selectedVibe)};
          color: white;
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: bold;
          box-shadow: 0 2px 6px rgba(0,0,0,0.3);
          white-space: nowrap;
        ">Start</div>
      `

      new mapboxgl.Marker({ element: startEl, anchor: 'bottom' })
        .setLngLat(coordinates[0])
        .setPopup(new mapboxgl.Popup({ offset: 25 }).setHTML('<h3>Starting Point</h3><p>Your walk begins here</p>'))
        .addTo(map.current)
    }

    // Fit map to route bounds
    const bounds = new mapboxgl.LngLatBounds()
    coordinates.forEach(coord => bounds.extend(coord))
    map.current.fitBounds(bounds, { padding: 50 })

  }, [routeData, selectedVibe])

  return <div ref={mapContainer} className="map" />
}
