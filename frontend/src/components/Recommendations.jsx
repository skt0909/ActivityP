import './Recommendations.css'

// Default recommendations shown before the user hits Apply
const DEFAULT_RECOMMENDATIONS = [
  {
    title:       'Increase Protein Bioavailability',
    category:    'Nutrition',
    icon:        '🍽️',
    color:       'nutrition',
    description: "Based on your metabolic burn, aim for 35 g of whey isolate or plant protein within the next 45 minutes to maximise muscle protein synthesis and recovery after today's high-intensity session.",
  },
  {
    title:       'Parasympathetic Breathing',
    category:    'Recovery',
    icon:        '🧘',
    color:       'recovery',
    description: "Your HRV is dipping below baseline. Engage in 10 minutes of guided 4-7-8 breathing to reset your nervous system for peak recovery. This will help transition your body into a restorative state faster.",
  },
  {
    title:       'Target Zone-2 Cardio',
    category:    'Performance',
    icon:        '💪',
    color:       'performance',
    description: "Today is optimised for endurance. Maintain a heart rate of 125-135 BPM for 40 minutes for mitochondrial health. This steady-state effort will build your aerobic base without overtaxing your recovery capacity.",
  },
]

function Recommendations({ recommendations }) {
  const items = recommendations && recommendations.length > 0
    ? recommendations
    : DEFAULT_RECOMMENDATIONS

  return (
    <section className="recommendations-section">
      <h2 className="section-title">Daily Optimization</h2>
      <div className="recommendations-list">
        {items.map((rec, idx) => (
          <div key={idx} className={`recommendation-card ${rec.color}`}>
            <div className="rec-icon">{rec.icon}</div>
            <div className="rec-content">
              <div className="rec-category">{rec.category}</div>
              <h3>{rec.title}</h3>
              <p>{rec.description}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

export default Recommendations
