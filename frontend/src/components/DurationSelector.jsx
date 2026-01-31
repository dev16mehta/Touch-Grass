/**
 * Duration selector component
 */
export const DurationSelector = ({ duration, onDurationChange }) => {
  const handleChange = (e) => {
    const value = Math.min(120, Math.max(10, parseInt(e.target.value) || 30))
    onDurationChange(value)
  }

  return (
    <div className="duration-selector">
      <h3>Walk Duration</h3>
      <div className="duration-input-group">
        <input
          type="number"
          min="10"
          max="120"
          step="5"
          value={duration}
          onChange={handleChange}
          className="duration-input"
        />
        <span className="duration-label">minutes</span>
      </div>
    </div>
  )
}
