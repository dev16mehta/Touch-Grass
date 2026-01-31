/**
 * Route information display component
 */
export const RouteInfo = ({ routeData, isCircular }) => {
  if (!routeData) return null

  return (
    <div className="route-info">
      <h3>Your {routeData.vibe} walk {routeData.config.emoji}</h3>

      <div className="route-stats">
        <div className="stat">
          <span className="stat-icon">📏</span>
          <span className="stat-value">{(routeData.route.distance / 1000).toFixed(2)} km</span>
        </div>
        <div className="stat">
          <span className="stat-icon">⏱️</span>
          <span className="stat-value">{routeData.route.duration} min</span>
        </div>
        <div className="stat">
          <span className="stat-icon">{isCircular ? '🔄' : '➡️'}</span>
          <span className="stat-value">{isCircular ? 'Circular' : 'One-way'}</span>
        </div>
      </div>

      <p className="route-description">{routeData.description}</p>

      <div className="places-list">
        <h4>Places on your route:</h4>
        {(routeData.waypoints || routeData.places || []).slice(0, 5).map((place, index) => (
          <div key={index} className="place-item">
            <span className="place-name">{place.name}</span>
            <span className="place-distance">{Math.round(place.distance)}m</span>
          </div>
        ))}
      </div>

      {routeData.directions && routeData.directions.steps && (
        <details className="directions-panel">
          <summary>Turn-by-turn directions ({routeData.directions.steps.length} steps)</summary>
          <div className="directions-list">
            {routeData.directions.steps.map((step, index) => (
              <div key={index} className="direction-step">
                <span className="step-number">{index + 1}</span>
                <div className="step-content">
                  <div className="step-instruction" dangerouslySetInnerHTML={{ __html: step.instruction }} />
                  <div className="step-meta">
                    {step.distance}m · {step.duration} min
                  </div>
                </div>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  )
}
