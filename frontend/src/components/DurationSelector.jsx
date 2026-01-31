/**
 * Duration selector component
 */
export const DurationSelector = ({ duration, onDurationChange }) => {
  const handleChange = (e) => {
    const value = e.target.value

    // Allow typing freely - just pass the value through
    if (value === '' || value === '-') {
      onDurationChange(value)
    } else {
      const numValue = parseInt(value)
      if (!isNaN(numValue)) {
        onDurationChange(numValue)
      }
    }
  }

  const handleBlur = (e) => {
    const value = e.target.value

    // When user leaves the field, validate and clamp
    if (value === '' || value === '-') {
      onDurationChange('')
      return
    }

    const numValue = parseInt(value)
    if (!isNaN(numValue)) {
      const clampedValue = Math.min(120, Math.max(10, numValue))
      onDurationChange(clampedValue)
    } else {
      onDurationChange('')
    }
  }

  const handleFocus = (e) => {
    e.target.select()
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
          onFocus={handleFocus}
          placeholder="e.g., 30"
          className="duration-input"
        />
        <span className="duration-label">minutes</span>
      </div>
    </div>
  )
}
