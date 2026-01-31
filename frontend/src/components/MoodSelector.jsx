/**
 * Mood selector component for detecting user vibe and location
 */
export const MoodSelector = ({
  moodText,
  onMoodTextChange,
  onDetect,
  detecting,
  detectedVibe,
  detectedLocation,
  onClearLocation
}) => {
  return (
    <div className="mood-selector">
      <h2>How are you feeling?</h2>
      <div className="mood-input-group">
        <textarea
          className="mood-input"
          placeholder="e.g., I want to relax in Central Park... or Date night in Kensington tonight!"
          value={moodText}
          onChange={(e) => onMoodTextChange(e.target.value)}
          rows="3"
        />
        <button
          className="detect-button"
          onClick={onDetect}
          disabled={detecting || !moodText.trim()}
        >
          {detecting ? 'Detecting...' : '✨ Detect Vibe'}
        </button>
      </div>

      {detectedVibe && (
        <div className="detected-vibe">
          <span className="detected-emoji">{detectedVibe.emoji}</span>
          <div className="detected-info">
            <span className="detected-name">{detectedVibe.vibe}</span>
            <span className="detected-desc">{detectedVibe.description}</span>
            {detectedLocation && (
              <span className="detected-location">
                📍 {detectedLocation.name || detectedLocation.formatted_address}
              </span>
            )}
          </div>
          {detectedLocation && onClearLocation && (
            <button
              className="clear-location-btn"
              onClick={onClearLocation}
              title="Use my current location instead"
            >
              ✕
            </button>
          )}
        </div>
      )}
    </div>
  )
}
