/**
 * Mood selector component for detecting user vibe
 */
export const MoodSelector = ({ moodText, onMoodTextChange, onDetect, detecting, detectedVibe }) => {
  return (
    <div className="mood-selector">
      <h2>How are you feeling?</h2>
      <div className="mood-input-group">
        <textarea
          className="mood-input"
          placeholder="e.g., I want to relax and unwind..."
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
          </div>
        </div>
      )}
    </div>
  )
}
