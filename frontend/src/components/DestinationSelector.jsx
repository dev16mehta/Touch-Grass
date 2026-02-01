/**
 * Destination selector for one-way routes
 */
import { MapPin, Loader2, X } from 'lucide-react'

export const DestinationSelector = ({ destination, onDestinationChange, onGeocode, geocoding, geocodedDest, onClearDest }) => {
  const handleGeocode = () => {
    if (destination.trim()) {
      onGeocode(destination)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && destination.trim()) {
      handleGeocode()
    }
  }

  return (
    <div className="destination-selector">
      <h3>Destination</h3>
      <div className="destination-input-group">
        <input
          type="text"
          value={destination}
          onChange={(e) => onDestinationChange(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="e.g., Trafalgar Square, London"
          className="destination-input"
        />
        <button
          onClick={handleGeocode}
          disabled={geocoding || !destination.trim()}
          className="geocode-button"
        >
          {geocoding ? <Loader2 size={16} className="spinning" /> : <MapPin size={16} />}
        </button>
      </div>

      {geocodedDest && (
        <div className="geocoded-destination">
          <div className="geocoded-info">
            <MapPin size={16} className="geocoded-icon" />
            <div className="geocoded-details">
              <span className="geocoded-address">{geocodedDest.formatted_address}</span>
            </div>
          </div>
          <button
            className="clear-dest-btn"
            onClick={onClearDest}
            title="Clear destination"
          >
            <X size={16} />
          </button>
        </div>
      )}
    </div>
  )
}
