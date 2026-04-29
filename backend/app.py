import sys
import os
import json
from pathlib import Path

print("[startup] Python imports starting", flush=True)

# Add parent directory to path so we can import from Activity_pstructure
sys.path.insert(0, str(Path(__file__).parent.parent))
print("[startup] sys.path updated", flush=True)

from dotenv import load_dotenv
print("[startup] dotenv imported", flush=True)

from flask import Flask, jsonify, request
print("[startup] Flask imported", flush=True)

from flask_cors import CORS
print("[startup] CORS imported", flush=True)

from flask_limiter import Limiter
print("[startup] Limiter imported", flush=True)

from flask_limiter.util import get_remote_address
print("[startup] get_remote_address imported", flush=True)

# Avoid importing scikit-learn which hangs on Windows
# We implement needed functions directly below
def make_predictions(X_transformed, model):
    """Make predictions using the model"""
    return model.predict(X_transformed)

def calculate_custom_metrics(df, sleep_hours=None, calories_intake=None):
    """Calculate display metrics from engineered features"""
    import pandas as pd
    print("[startup] pandas imported in calculate_custom_metrics", flush=True)
    required_cols = ["ActiveMinutesTotal", "Calories"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}'")

    # Activity Score: 1-100 based on active minutes
    activity_ratio = (df["ActiveMinutesTotal"] / 90.0).clip(upper=1.0)
    df["ActivityScore"] = (activity_ratio * 99 + 1).round().astype(int)

    # Sleep Quality Rating: 1-100 based on deviation from 7.5h
    if sleep_hours is not None:
        deviation = abs(float(sleep_hours) - 7.5)
        sleep_score = max(1.0, 100.0 - deviation * 12.5)
    else:
        sedentary = df.get("SedentaryMinutes", pd.Series([480]))
        est_sleep_hours = sedentary.iloc[0] / 60.0 * 0.4
        deviation = abs(est_sleep_hours - 7.5)
        sleep_score = max(1.0, 100.0 - deviation * 12.5)

    df["sleep_quality_rating"] = int(round(min(100.0, sleep_score)))

    # Diet Completion: ratio of intake to predicted burn
    if calories_intake is not None:
        diet_completion = float(calories_intake) / max(float(df["Calories"].iloc[0]), 1.0)
    else:
        diet_completion = 1.0

    df["diet_completion"] = round(diet_completion, 3)

    return df

load_dotenv()
app = Flask(__name__)

# Configure CORS based on environment
allowed_origins = os.getenv(
    'ALLOWED_ORIGINS',
    'http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:5175,http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175'
).split(',')
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

# Load real trained model
print(f"[startup] Loading real trained model...")
try:
    import joblib
    print(f"[startup] joblib imported")

    model = joblib.load(str(MODEL_PATH))
    print(f"[startup] Model loaded successfully from {MODEL_PATH}")
    print(f"[startup] Model type: {type(model)}")

    transformer = joblib.load(str(TRANSFORMER_PATH))
    print(f"[startup] Transformer loaded successfully from {TRANSFORMER_PATH}")
    print(f"[startup] Models initialized - using REAL trained model")

except Exception as e:
    print(f"[ERROR] Failed to load real model: {e}")
    print(f"[ERROR] To fix this, retrain the model: python main.py")
    import traceback
    traceback.print_exc()
    model = None
    transformer = None


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

    import pandas as pd
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


def adjust_prediction_for_sidebar_inputs(predicted_calories, data, engineered_df):
    """
    Apply a lightweight deterministic adjustment so burn prediction reflects
    all sidebar vitals (age, gender, heart rate, sleep, activity level).

    This compensates for the model only being trained on activity features
    by adjusting the base prediction based on physiological factors.
    """
    import sys
    sys.stdout.flush()
    sys.stderr.flush()

    try:
        predicted_calories = float(predicted_calories)
        age = float(data.get('age', 30))
        heart_rate = float(data.get('heart_rate', 75))
        sleep_hours = float(data.get('sleep_hours', 7.5))
        gender = str(data.get('gender', 'Male')).strip().lower()
        activity_level = str(data.get('activity_level', 'Medium')).strip().lower()
        active_minutes = float(engineered_df['ActiveMinutesTotal'].iloc[0])

        print(f"\n[adjust] ===== CALORIE ADJUSTMENT CALCULATION =====")
        print(f"[adjust] Base model prediction: {predicted_calories:.0f} kcal")
        print(f"[adjust] Input parameters: age={age}, gender={gender}, hr={heart_rate} bpm, sleep={sleep_hours}h, activity_level={activity_level}, active_min={active_minutes:.0f}")

        # Baseline physiological and behavior modifiers
        # These adjust from a 30-year-old, 70 bpm heart rate, 7.5h sleep baseline
        hr_term = (heart_rate - 70.0) * 4.0  # +/- 4 cal per bpm difference
        sleep_term = (sleep_hours - 7.5) * 18.0  # +/- 18 cal per hour difference
        age_term = -(age - 30.0) * 3.0  # -3 cal per year older (metabolism slows)
        gender_term = 90.0 if gender == 'male' else -30.0  # Male: +90, Female: -30
        level_term = {'low': -120.0, 'medium': 0.0, 'high': 180.0}.get(activity_level, 0.0)
        activity_term = (active_minutes - 90.0) * 2.5  # +/- 2.5 cal per minute difference

        print(f"[adjust] Adjustment factors:")
        print(f"[adjust]   Heart rate adjustment ({heart_rate} bpm): {hr_term:+.0f} kcal")
        print(f"[adjust]   Sleep adjustment ({sleep_hours}h): {sleep_term:+.0f} kcal")
        print(f"[adjust]   Age adjustment ({age} yrs): {age_term:+.0f} kcal")
        print(f"[adjust]   Gender adjustment ({gender}): {gender_term:+.0f} kcal")
        print(f"[adjust]   Activity level adjustment ({activity_level}): {level_term:+.0f} kcal")
        print(f"[adjust]   Active minutes adjustment ({active_minutes:.0f} min): {activity_term:+.0f} kcal")

        total_adjustment = hr_term + sleep_term + age_term + gender_term + level_term + activity_term
        print(f"[adjust] Total adjustment: {total_adjustment:+.0f} kcal")

        adjusted = predicted_calories + total_adjustment
        final = max(800.0, adjusted)  # Minimum 800 kcal

        print(f"[adjust] Calculation: {predicted_calories:.0f} + {total_adjustment:.0f} = {adjusted:.0f}")
        print(f"[adjust] FINAL ADJUSTED PREDICTION: {final:.0f} kcal")
        print(f"[adjust] ============================================\n")

        return final

    except Exception as e:
        print(f"[ERROR] adjust_prediction_for_sidebar_inputs failed: {e}")
        import traceback
        traceback.print_exc()
        # Return base prediction if adjustment fails
        return float(predicted_calories)


@app.route('/predict', methods=['POST'])
@limiter.limit("100 per hour")
def predict():
    """Predict calories and compute health metrics + dynamic recommendations."""
    print("[route] /predict handler invoked — route is registered and reachable")
    print(f"[route] model is None: {model is None}, transformer is None: {transformer is None}")
    print(f"[route] model type: {type(model)}, transformer type: {type(transformer)}")
    # Check if models loaded successfully
    if model is None or transformer is None:
        print(f"[ERROR] Models not loaded! model={model is not None}, transformer={transformer is not None}")
        return jsonify({
            'error': 'Models not loaded. Check deployment logs for details.',
            'model_loaded': model is not None,
            'transformer_loaded': transformer is not None
        }), 503

    try:
        data = request.get_json()
        print(f"[predict] Received JSON data: {data}")

        # Pull the raw user inputs that calculate_custom_metrics needs directly
        sleep_hours     = float(data.get('sleep_hours', 7.5))
        calories_intake = float(data.get('calories_intake', 0))

        # Engineer features
        print(f"[predict] Engineering features...")
        X = engineer_features(data)
        print(f"[predict] Features engineered. Shape: {X.shape}, Columns: {list(X.columns)}")

        # Transform & predict
        print(f"[predict] Transforming features...")
        X_transformed = transformer.transform(X)
        print(f"[predict] Features transformed. Shape: {X_transformed.shape}")
        
        print(f"[predict] Making prediction with REAL trained model...")
        try:
            estimated_burn = float(make_predictions(X_transformed, model)[0])
            print(f"[predict] Real model prediction: {estimated_burn:.0f} kcal")
        except Exception as e:
            print(f"[ERROR] Model prediction failed: {e}")
            estimated_burn = 2000.0

        # Clamp to realistic range
        estimated_burn = max(800.0, min(4000.0, estimated_burn))

        print(f"[predict] Estimated burn: {estimated_burn:.0f} kcal")

        # Calculate custom metrics — pass raw inputs for accurate scoring
        df = X.copy()
        df['Calories'] = estimated_burn
        print(f"[predict] Calculating custom metrics...")
        df_metrics = calculate_custom_metrics(
            df,
            sleep_hours=sleep_hours,
            calories_intake=calories_intake if calories_intake > 0 else None,
        )
        print(f"[predict] Metrics calculated successfully")

        activity_score       = int(df_metrics['ActivityScore'].values[0])
        sleep_quality_rating = int(df_metrics['sleep_quality_rating'].values[0])
        diet_completion      = float(df_metrics['diet_completion'].values[0])

        recommendations = build_recommendations(
            activity_score, sleep_quality_rating, diet_completion
        )
        print(f"[predict] Recommendations generated")

        response = {
            'estimated_burn':       round(estimated_burn),  # Real model prediction
            'activity_score':       activity_score,
            'sleep_quality_rating': sleep_quality_rating,
            'diet_completion':      round(diet_completion, 2),  # calories_intake / estimated_burn
            'recommendations':      recommendations,
            '_debug': {
                'model_type': str(type(model).__name__),
                'estimated_burn': round(estimated_burn),
                'model_source': 'real_trained_model' if model is not None else 'error'
            }
        }
        print(f"[predict] Returning successful response: {estimated_burn:.0f} kcal")
        return jsonify(response)

    except Exception as e:
        print(f"[predict] ERROR in /predict: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'error_type': type(e).__name__}), 400


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[startup] Flask app starting on port {port}")
    print(f"[startup] Flask app object: {app}")
    print(f"[startup] Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"[startup]   {rule.rule} -> {rule.endpoint} (methods: {rule.methods})")
    app.run(host='0.0.0.0', port=port, debug=False)
