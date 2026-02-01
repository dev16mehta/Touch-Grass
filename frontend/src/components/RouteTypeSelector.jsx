/**
 * Route type selector (circular vs one-way)
 */
import { RotateCw, MoveRight } from 'lucide-react'

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
          {isCircular ? (
            <>
              <RotateCw size={16} /> Circular route (return to start)
            </>
          ) : (
            <>
              <MoveRight size={16} /> One-way route
            </>
          )}
        </span>
      </label>
    </div>
  )
}
