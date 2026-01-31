/**
 * Duration selector component
 */
export const DurationSelector = ({ duration, onDurationChange }) => {
  const handleChange = (e) => {
    const value = e.target.value
    // Allow empty string or any number
    if (value === '') {
      onDurationChange('')
    } else {
      const numValue = parseInt(value)
      if (!isNaN(numValue)) {
        onDurationChange(numValue)
      }
    }
  }

  const handleBlur = (e) => {
    const value = e.target.value
    // When user leaves field, clamp to valid range if needed
    if (value === '') {
      return
    }
    const numValue = parseInt(value)
    if (!isNaN(numValue)) {
      const clampedValue = Math.min(120, Math.max(10, numValue))
      onDurationChange(clampedValue)
    }
  }

  return (
    <div className="duration-selector">
      <h3>Walk Duration</h3>
      <div className="duration-input-group">
        <input
          type="number"
          min="10"
          max="120"
          step="1"
          value={duration}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="e.g., 30"
          className="duration-input"
        />
        <span className="duration-label">minutes</span>
      </div>
    </div>
  )
}
