import { useState } from 'react'
import './Sidebar.css'

/**
 * Derive the activity-minute breakdown from high-level sidebar inputs.
 * These must match the feature engineering logic in backend/app.py.
 *
 * Step estimation is anchored to realistic activity_level baselines
 * (Low ≈ 4 k steps, Medium ≈ 8 k, High ≈ 13 k) and modulated ±20%
 * by heart-rate intensity so every slider change produces a different result.
 *
 * NOTE: `calories` is INTAKE, not burn — it is NOT used to estimate steps.
 */
function deriveActivityInputs(inputs) {
  const { calories, heart_rate, sleep_hours, activity_level } = inputs

  // Intensity ratio from heart rate: 60 bpm (rest) → 150 bpm (max effort)
  const intensity = Math.max(0, Math.min(1, (heart_rate - 60) / 90))

  // Activity-level baseline steps, adjusted ±20% by HR intensity
  const baseSteps = { Low: 4000, Medium: 8000, High: 13000 }
  const total_steps = Math.round(baseSteps[activity_level] * (0.8 + 0.4 * intensity))

  // Active minutes from steps at an average pace (85 steps/min)
  const active_minutes_total = Math.max(15, Math.round(total_steps / 85))

  const very_active_minutes   = Math.round(active_minutes_total * (0.12 + 0.35 * intensity))
  const fairly_active_minutes = Math.round(active_minutes_total * (0.08 + 0.22 * intensity))
  const lightly_active_minutes = Math.max(
    0,
    active_minutes_total - very_active_minutes - fairly_active_minutes
  )

  // Awake hours minus active time = sedentary
  const awake_minutes    = Math.round((24 - sleep_hours) * 60)
  const sedentary_minutes = Math.max(0, awake_minutes - active_minutes_total)

  return {
    age: inputs.age,
    gender: inputs.gender,
    activity_level,
    total_steps,
    very_active_minutes,
    fairly_active_minutes,
    lightly_active_minutes,
    sedentary_minutes,
    sleep_hours,
    calories_intake: calories,
  }
}

function Sidebar({ onPredict, loading }) {
  const [inputs, setInputs] = useState({
    age: 28,
    calories: 2200,
    heart_rate: 75,
    sleep_hours: 7,
    gender: 'Male',
    activity_level: 'Medium',
  })

  const handleSliderChange = (field, value) => {
    setInputs(prev => ({ ...prev, [field]: Number(value) }))
  }

  const handleSelectChange = (field, value) => {
    setInputs(prev => ({ ...prev, [field]: value }))
  }

  const handleApply = () => {
    const payload = deriveActivityInputs(inputs)
    onPredict(payload)
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-content">
        <div className="sidebar-header">
          <div className="header-icon">📊</div>
          <div>
            <h2>Daily Vitals</h2>
            <p>Syncing biometric pulse</p>
          </div>
        </div>

        <div className="vitals-group">
          <div className="vital-item">
            <div className="vital-label">
              <span>👤 Age</span>
              <span className="vital-value">{inputs.age}</span>
            </div>
            <input
              type="range"
              min="18"
              max="80"
              value={inputs.age}
              onChange={e => handleSliderChange('age', e.target.value)}
            />
          </div>

          <div className="vital-item">
            <div className="vital-label">
              <span>🔥 Calories</span>
              <span className="vital-value">{inputs.calories}</span>
            </div>
            <input
              type="range"
              min="800"
              max="5000"
              step="50"
              value={inputs.calories}
              onChange={e => handleSliderChange('calories', e.target.value)}
            />
          </div>

          <div className="vital-item">
            <div className="vital-label">
              <span>❤️ Heart Rate</span>
              <span className="vital-value">{inputs.heart_rate} bpm</span>
            </div>
            <input
              type="range"
              min="40"
              max="140"
              value={inputs.heart_rate}
              onChange={e => handleSliderChange('heart_rate', e.target.value)}
            />
          </div>

          <div className="vital-item">
            <div className="vital-label">
              <span>😴 Sleep Hours</span>
              <span className="vital-value">{inputs.sleep_hours} h</span>
            </div>
            <input
              type="range"
              min="0"
              max="12"
              step="0.5"
              value={inputs.sleep_hours}
              onChange={e => handleSliderChange('sleep_hours', e.target.value)}
            />
          </div>

          <div className="select-group">
            <label>Gender</label>
            <select value={inputs.gender} onChange={e => handleSelectChange('gender', e.target.value)}>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
            </select>
          </div>

          <div className="select-group">
            <label>Activity Level</label>
            <select value={inputs.activity_level} onChange={e => handleSelectChange('activity_level', e.target.value)}>
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
            </select>
          </div>
        </div>

        <button
          className="apply-btn"
          onClick={handleApply}
          disabled={loading}
        >
          {loading ? 'Computing...' : 'Apply'}
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
