import sys
import os
import json
import pandas as pd
from pathlib import Path

# Add parent directory to path so we can import from Activity_pstructure
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from Activity_pstructure.utils.inference_utils import (
    load_model,
    load_transformer,
    make_predictions,
    calculate_custom_metrics
)

app = Flask(__name__)

# Configure CORS based on environment
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, origins=allowed_origins, supports_credentials=True)

# Configure rate limiting: 100 requests per hour per IP
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="memory://"
)

# Load model and transformer once at startup
MODEL_PATH = Path(__file__).parent.parent / 'model' / 'model.pkl'
TRANSFORMER_PATH = Path(__file__).parent.parent / 'model' / 'transformer.pkl'

print(f"[startup] Attempting to load model from: {MODEL_PATH}")
print(f"[startup] Model file exists: {MODEL_PATH.exists()}")
print(f"[startup] Attempting to load transformer from: {TRANSFORMER_PATH}")
print(f"[startup] Transformer file exists: {TRANSFORMER_PATH.exists()}")

model = None
transformer = None

try:
    model = load_model(str(MODEL_PATH))
    print("[startup] Model loaded successfully")
except Exception as e:
    print(f"[startup] ERROR loading model: {e}")
    import traceback
    traceback.print_exc()

try:
    transformer = load_transformer(str(TRANSFORMER_PATH))
    print("[startup] Transformer loaded successfully")
except Exception as e:
    print(f"[startup] ERROR loading transformer: {e}")
    import traceback
    traceback.print_exc()


def engineer_features(data):
    """
    Engineer all 29 transformer columns from user input.

    Frontend sends:
        age, gender, activity_level,
        total_steps, very_active_minutes, fairly_active_minutes,
        lightly_active_minutes, sedentary_minutes,
        sleep_hours, calories_intake
    """
    total_steps        = float(data['total_steps'])
    very_active_min    = float(data['very_active_minutes'])
    fairly_active_min  = float(data['fairly_active_minutes'])
    lightly_active_min = float(data['lightly_active_minutes'])
    sedentary_min      = float(data['sedentary_minutes'])

    # --- Derived distance features ---
    total_distance              = total_steps * 0.000762
    very_active_distance        = very_active_min    * 0.10
    moderately_active_distance  = fairly_active_min  * 0.06
    light_active_distance       = lightly_active_min * 0.03
    sedentary_active_distance   = 0.0

    active_minutes_total = very_active_min + fairly_active_min + lightly_active_min

    steps_per_minute   = total_steps / max(active_minutes_total, 1)
    distance_per_step  = total_distance / max(total_steps, 1)
    very_active_ratio  = very_active_min / max(active_minutes_total, 1)
    sedentary_ratio    = sedentary_min / max(sedentary_min + active_minutes_total, 1)

    activity_score       = min((active_minutes_total / 150.0), 1.0) * 99 + 1
    effective_active_time = very_active_min * 2 + fairly_active_min

    engineered = {
        'TotalSteps':                      total_steps,
        'TotalDistance':                   total_distance,
        'TrackerDistance':                 total_distance,
        'VeryActiveDistance':              very_active_distance,
        'ModeratelyActiveDistance':        moderately_active_distance,
        'LightActiveDistance':             light_active_distance,
        'SedentaryActiveDistance':         sedentary_active_distance,
        'VeryActiveMinutes':               very_active_min,
        'FairlyActiveMinutes':             fairly_active_min,
        'LightlyActiveMinutes':            lightly_active_min,
        'SedentaryMinutes':                sedentary_min,
        'StepsPerMinute':                  steps_per_minute,
        'DistancePerStep':                 distance_per_step,
        'VeryActiveRatio':                 very_active_ratio,
        'SedentaryRatio':                  sedentary_ratio,
        'ActiveMinutesTotal':              active_minutes_total,
        'ActivityScore':                   activity_score,
        'EffectiveActiveTime':             effective_active_time,
        'ActivityLevel':                   data['activity_level'],
        'Gender':                          data['gender'],
        'Age':                             float(data['age']),
        'VeryActiveDistance_norm':         very_active_distance,
        'ModeratelyActiveDistance_norm':   moderately_active_distance,
        'SedentaryActiveDistance_norm':    sedentary_active_distance,
        'VeryActiveMinutes_norm':          very_active_min,
        'FairlyActiveMinutes_norm':        fairly_active_min,
        'StepsPerMinute_norm':             steps_per_minute,
        'DistancePerStep_norm':            distance_per_step,
        'VeryActiveRatio_norm':            very_active_ratio,
    }

    return pd.DataFrame([engineered])


def build_recommendations(activity_score, sleep_rating, diet_completion):
    """
    Return dynamic recommendation text based on the computed metrics,
    matching the three Stitch recommendation rows:
      Nutrition  / Recovery / Performance
    """
    # ── Nutrition (calorie / diet balance) ──────────────────────────────
    if diet_completion > 1.15:
        nutrition_title = "Reduce Caloric Surplus"
        nutrition_body  = (
            "You consumed significantly more than your predicted burn. "
            "Prioritise lean protein and fibre-dense vegetables to stay satiated "
            "without excess energy."
        )
    elif diet_completion < 0.85:
        nutrition_title = "Increase Protein Bioavailability"
        nutrition_body  = (
            "Your intake is below predicted burn. Aim for 35 g of whey isolate or "
            "plant protein to maximise muscle-protein synthesis and fuel recovery."
        )
    else:
        nutrition_title = "Maintain Your Nutrition Balance"
        nutrition_body  = (
            "Energy intake is well aligned with predicted burn. Keep prioritising "
            "whole foods, complex carbs, and lean protein to sustain performance."
        )

    # ── Recovery (sleep quality) ─────────────────────────────────────────
    if sleep_rating < 60:
        recovery_title = "Prioritise Deep Sleep"
        recovery_body  = (
            "Sleep quality is below optimal. Engage in 10 minutes of guided 4-7-8 "
            "breathing before bed to activate your parasympathetic nervous system "
            "and extend deep-sleep cycles."
        )
    elif sleep_rating < 80:
        recovery_title = "Optimise Your Sleep Window"
        recovery_body  = (
            "Sleep is adequate but not peak. Try shifting bedtime 30 minutes earlier "
            "and avoiding blue-light exposure for an hour before sleep."
        )
    else:
        recovery_title = "Sleep Recovery is Excellent"
        recovery_body  = (
            "HRV and sleep quality are in the optimal zone. Your nervous system is "
            "primed for high-intensity work today. Keep your sleep schedule consistent."
        )

    # ── Performance (activity score) ─────────────────────────────────────
    if activity_score < 50:
        performance_title = "Build Your Aerobic Base"
        performance_body  = (
            "Activity is below threshold. Start with a 20-minute Zone-2 walk "
            "(heart rate 100-120 BPM) to begin building mitochondrial density "
            "without overtaxing your system."
        )
    elif activity_score < 80:
        performance_title = "Target Zone-2 Cardio"
        performance_body  = (
            "Today is optimised for endurance. Maintain 125-135 BPM for 40 minutes "
            "for mitochondrial health. This steady-state effort builds aerobic base "
            "without overtaxing recovery capacity."
        )
    else:
        performance_title = "Peak Performance Achieved"
        performance_body  = (
            "Exceptional activity level. Ensure at least 48 hours before your next "
            "high-intensity session. Active recovery (yoga, light swim) will maintain "
            "performance without accumulating fatigue."
        )

    return [
        {
            "title":       nutrition_title,
            "category":    "Nutrition",
            "icon":        "🍽️",
            "color":       "nutrition",
            "description": nutrition_body,
        },
        {
            "title":       recovery_title,
            "category":    "Recovery",
            "icon":        "🧘",
            "color":       "recovery",
            "description": recovery_body,
        },
        {
            "title":       performance_title,
            "category":    "Performance",
            "icon":        "💪",
            "color":       "performance",
            "description": performance_body,
        },
    ]


@app.route('/predict', methods=['POST'])
@limiter.limit("100 per hour")
def predict():
    """Predict calories and compute health metrics + dynamic recommendations."""
    print("[/predict] Route handler called - request received")
    # Check if models loaded successfully
    if model is None or transformer is None:
        return jsonify({
            'error': 'Models not loaded. Check deployment logs for details.',
            'model_loaded': model is not None,
            'transformer_loaded': transformer is not None
        }), 503

    try:
        data = request.get_json()

        # Pull the raw user inputs that calculate_custom_metrics needs directly
        sleep_hours     = float(data.get('sleep_hours', 7.5))
        calories_intake = float(data.get('calories_intake', 0))

        # Engineer features
        X = engineer_features(data)

        # Transform & predict
        X_transformed = transformer.transform(X)
        predicted_calories = float(make_predictions(X_transformed, model)[0])

        # Calculate custom metrics — pass raw inputs for accurate scoring
        df = X.copy()
        df['Calories'] = predicted_calories
        df_metrics = calculate_custom_metrics(
            df,
            sleep_hours=sleep_hours,
            calories_intake=calories_intake if calories_intake > 0 else None,
        )

        activity_score       = int(df_metrics['ActivityScore'].values[0])
        sleep_quality_rating = int(df_metrics['sleep_quality_rating'].values[0])
        diet_completion      = float(df_metrics['diet_completion'].values[0])

        recommendations = build_recommendations(
            activity_score, sleep_quality_rating, diet_completion
        )

        return jsonify({
            'predicted_calories':   round(predicted_calories),
            'activity_score':       activity_score,
            'sleep_quality_rating': sleep_quality_rating,
            'diet_completion':      round(diet_completion, 2),
            'recommendations':      recommendations,
        })

    except Exception as e:
        print(f"Error in /predict: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    # Diagnostic: log resolved port
    print(f"[startup] Resolved port: {port}")

    # Diagnostic: log Flask app and all registered routes
    print(f"[startup] Flask app: {app}")
    print(f"[startup] Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"[startup]   {rule.rule} -> {rule.endpoint} (methods: {rule.methods})")

    app.run(host='0.0.0.0', port=port, debug=False)
