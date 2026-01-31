/**
 * Route type selector (circular vs one-way)
 */
export const RouteTypeSelector = ({ isCircular, onToggle }) => {
  return (
    <div className="route-type-selector">
      <label className="toggle-label">
        <input
          type="checkbox"
          checked={isCircular}
          onChange={(e) => onToggle(e.target.checked)}
        />
        <span className="toggle-text">
          {isCircular ? '🔄 Circular route (return to start)' : '➡️ One-way route'}
        </span>
      </label>
    </div>
  )
}
