import './MetricCard.css'

function MetricCard({ title, value, type, icon, trend, unit }) {
  const renderCardContent = () => {
    switch (type) {
      case 'activity':
        return <ActivityScoreCard value={value} trend={trend} />
      case 'sleep':
        return <SleepScoreCard value={value} />
      case 'burn':
        return <PredictedBurnCard value={value} unit={unit} />
      default:
        return null
    }
  }

  return (
    <div className="metric-card">
      <div className="card-header">
        <h3>{title}</h3>
        {trend && <div className="trend-badge">📈 {trend}</div>}
      </div>
      {renderCardContent()}
    </div>
  )
}

function ActivityScoreCard({ value, trend }) {
  const circumference = 251.2
  const offset = circumference - (value / 100) * circumference

  return (
    <div className="card-content activity-score">
      <div className="progress-ring-container">
        <svg viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="40" className="progress-ring-bg" />
          <circle
            cx="50"
            cy="50"
            r="40"
            className="progress-ring"
            style={{ strokeDashoffset: offset }}
          />
        </svg>
        <div className="progress-value">
          <div className="big-number">{value}</div>
          <div className="unit">Percent</div>
        </div>
      </div>
      <p className="card-description">Systematic load training is exceeding monthly benchmarks.</p>
    </div>
  )
}

function SleepScoreCard({ value }) {
  // Generate 7 random bars (representing a week)
  const bars = [40, 65, 85, 95, 70, 50, 60]

  return (
    <div className="card-content sleep-score">
      <div className="sleep-value">
        <div className="big-number">{value}<span className="unit-inline">%</span></div>
      </div>
      <div className="sleep-bars">
        {bars.map((height, idx) => (
          <div key={idx} className="bar" style={{ height: `${height}%` }} />
        ))}
      </div>
      <div className="sleep-labels">
        <span>Mon</span>
        <span>Today</span>
        <span>Sun</span>
      </div>
    </div>
  )
}

function PredictedBurnCard({ value, unit }) {
  const display = Number.isFinite(value)
    ? (value >= 1000 ? `${(value / 1000).toFixed(1)}k` : `${Math.round(value)}`)
    : '--'

  return (
    <div className="card-content burn-card">
      <div className="burn-value">
        <div className="big-number">{display}</div>
        <div className="unit">{unit || 'KCAL'} REMAINING</div>
      </div>
      <svg className="wave-decoration" viewBox="0 0 400 100" preserveAspectRatio="none">
        <defs>
          <linearGradient id="waveGradient" x1="0%" x2="0%" y1="0%" y2="100%">
            <stop offset="0%" stopColor="#6bfe9c" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#6bfe9c" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d="M0 80 C 50 70, 100 90, 150 80 C 200 70, 250 40, 300 50 C 350 60, 400 30, 450 40 L 450 100 L 0 100 Z" fill="url(#waveGradient)" />
        <path d="M0 80 C 50 70, 100 90, 150 80 C 200 70, 250 40, 300 50 C 350 60, 400 30, 450 40" fill="none" stroke="#6bfe9c" strokeWidth="3" />
      </svg>
      <p className="card-description">Optimal zone for metabolic efficiency.</p>
    </div>
  )
}

export default MetricCard
