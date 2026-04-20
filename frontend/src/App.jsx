import { useState } from 'react'
import Sidebar from './components/Sidebar'
import MetricCard from './components/MetricCard'
import Recommendations from './components/Recommendations'
import './App.css'

function App() {
  const [metrics, setMetrics] = useState({
    predicted_calories:  0,
    activity_score:      0,
    sleep_quality_rating: 0,
    diet_completion:     0,
    recommendations:     [],
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handlePredict = async (inputData) => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('http://localhost:5000/predict', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(inputData),
      })

      if (!response.ok) {
        const errBody = await response.json()
        throw new Error(errBody.error || `HTTP ${response.status}`)
      }

      const data = await response.json()
      setMetrics(data)
    } catch (err) {
      console.error('Prediction error:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <Sidebar onPredict={handlePredict} loading={loading} />
      <main className="main-content">
        <header className="dashboard-header">
          <h1>Health Metrics <span className="highlight">Dashboard</span></h1>
          <p>Your biometric blueprint is optimized. Performance trends indicate high recovery readiness for today's scheduled peak loads.</p>
        </header>

        {error && (
          <div style={{
            background: 'rgba(255,110,133,0.10)',
            border: '1px solid rgba(255,110,133,0.30)',
            borderRadius: '0.75rem',
            padding: '0.75rem 1.25rem',
            marginBottom: '1.5rem',
            color: '#ff6e85',
            fontSize: '0.85rem',
            fontFamily: 'Inter, sans-serif',
          }}>
            ⚠️ Could not reach the backend: {error}
          </div>
        )}

        <section className="metrics-grid">
          <MetricCard
            title="Activity Score"
            value={metrics.activity_score}
            type="activity"
            icon="trending_up"
            trend="+12%"
          />
          <MetricCard
            title="Sleep Score"
            value={metrics.sleep_quality_rating}
            type="sleep"
            icon="nights_stay"
          />
          <MetricCard
            title="Predicted Burn"
            value={metrics.predicted_calories}
            type="burn"
            icon="bolt"
            unit="KCAL"
          />
        </section>

        <Recommendations recommendations={metrics.recommendations} />
      </main>
    </div>
  )
}

export default App
