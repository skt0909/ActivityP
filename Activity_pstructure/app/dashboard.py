import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Activity_pstructure.utils.inference_utils import (  # noqa: E402
    load_model,
    load_transformer,
    make_predictions,
    transform_data,
)

TRANSFORMER_PATH = PROJECT_ROOT / "model" / "transformer.pkl"
MODEL_PATH = PROJECT_ROOT / "model" / "model.pkl"

MODEL_FEATURES = [
    "TotalSteps",
    "TotalDistance",
    "TrackerDistance",
    "VeryActiveDistance",
    "ModeratelyActiveDistance",
    "LightActiveDistance",
    "SedentaryActiveDistance",
    "VeryActiveMinutes",
    "FairlyActiveMinutes",
    "LightlyActiveMinutes",
    "SedentaryMinutes",
    "StepsPerMinute",
    "DistancePerStep",
    "VeryActiveRatio",
    "SedentaryRatio",
    "ActiveMinutesTotal",
    "ActivityScore",
    "EffectiveActiveTime",
    "ActivityLevel",
    "Gender",
    "Age",
    "VeryActiveDistance_norm",
    "ModeratelyActiveDistance_norm",
    "SedentaryActiveDistance_norm",
    "VeryActiveMinutes_norm",
    "FairlyActiveMinutes_norm",
    "StepsPerMinute_norm",
    "DistancePerStep_norm",
    "VeryActiveRatio_norm",
]


@st.cache_resource
def load_artifacts():
    transformer = load_transformer(str(TRANSFORMER_PATH))
    model = load_model(str(MODEL_PATH))
    return transformer, model


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def build_features(
    age: int,
    steps: int,
    heart_rate: int,
    sleep_hours: float,
    calories: int,
) -> pd.DataFrame:
    total_distance = steps * 0.0008
    tracker_distance = total_distance * 1.03

    activity_intensity = clamp01((heart_rate - 60) / 90)
    very_active_ratio = 0.12 + 0.35 * activity_intensity
    fairly_active_ratio = 0.08 + 0.22 * activity_intensity

    active_minutes_total = int(round(max(15, steps / 85)))
    very_active_minutes = int(round(active_minutes_total * very_active_ratio))
    fairly_active_minutes = int(round(active_minutes_total * fairly_active_ratio))
    lightly_active_minutes = int(
        max(0, active_minutes_total - very_active_minutes - fairly_active_minutes)
    )
    sedentary_minutes = int(
        max(0, (24 - sleep_hours) * 60 - active_minutes_total)
    )

    if steps < 5000:
        activity_level = "Low"
    elif steps < 10000:
        activity_level = "Medium"
    else:
        activity_level = "High"

    very_active_distance = total_distance * (0.18 + 0.32 * activity_intensity)
    moderately_active_distance = total_distance * (0.20 + 0.25 * activity_intensity)
    light_active_distance = max(
        0.0, total_distance - very_active_distance - moderately_active_distance
    )
    sedentary_active_distance = total_distance * 0.03

    steps_per_minute = steps / max(1, active_minutes_total)
    distance_per_step = total_distance / max(1, steps)
    sedentary_ratio = sedentary_minutes / 1440
    effective_active_time = active_minutes_total / max(1, active_minutes_total + sedentary_minutes)
    activity_score = max(1, min(100, int(round((active_minutes_total / 150) * 100))))

    row = {
        "TotalSteps": float(steps),
        "TotalDistance": float(total_distance),
        "TrackerDistance": float(tracker_distance),
        "VeryActiveDistance": float(very_active_distance),
        "ModeratelyActiveDistance": float(moderately_active_distance),
        "LightActiveDistance": float(light_active_distance),
        "SedentaryActiveDistance": float(sedentary_active_distance),
        "VeryActiveMinutes": float(very_active_minutes),
        "FairlyActiveMinutes": float(fairly_active_minutes),
        "LightlyActiveMinutes": float(lightly_active_minutes),
        "SedentaryMinutes": float(sedentary_minutes),
        "StepsPerMinute": float(steps_per_minute),
        "DistancePerStep": float(distance_per_step),
        "VeryActiveRatio": float(very_active_ratio),
        "SedentaryRatio": float(sedentary_ratio),
        "ActiveMinutesTotal": float(active_minutes_total),
        "ActivityScore": float(activity_score),
        "EffectiveActiveTime": float(effective_active_time),
        "ActivityLevel": activity_level,
        "Gender": "Male",
        "Age": float(age),
        "VeryActiveDistance_norm": clamp01(very_active_distance / 5.0),
        "ModeratelyActiveDistance_norm": clamp01(moderately_active_distance / 4.0),
        "SedentaryActiveDistance_norm": clamp01(sedentary_active_distance / 1.0),
        "VeryActiveMinutes_norm": clamp01(very_active_minutes / 120.0),
        "FairlyActiveMinutes_norm": clamp01(fairly_active_minutes / 120.0),
        "StepsPerMinute_norm": clamp01(steps_per_minute / 120.0),
        "DistancePerStep_norm": clamp01(distance_per_step / 0.002),
        "VeryActiveRatio_norm": clamp01(very_active_ratio),
    }

    return pd.DataFrame([[row[col] for col in MODEL_FEATURES]], columns=MODEL_FEATURES)


def sleep_score(sleep_hours: float) -> int:
    score = int(round(max(0.0, 100.0 - abs(7.5 - sleep_hours) * 15.0)))
    return max(1, min(100, score))


def recommendations(activity_score_value: int, sleep_score_value: int, cal_gap: float):
    items = []
    if activity_score_value < 60:
        items.append("Add a 20-30 minute brisk walk to lift daily activity.")
    if sleep_score_value < 70:
        items.append("Target 7-8 hours of sleep and keep a fixed sleep schedule.")
    if cal_gap > 250:
        items.append("You consumed more calories than predicted burn; consider lighter dinner portions.")
    elif cal_gap < -250:
        items.append("You are below predicted burn; add a balanced snack or recovery meal.")
    if not items:
        items.append("Great balance today. Keep the same routine for consistency.")
    return items


st.set_page_config(page_title="Health Metrics Dashboard", layout="wide")
st.title("Health Metrics Dashboard")
st.caption("Simple daily scores from your activity profile")

st.sidebar.header("Daily Inputs")
age = st.sidebar.slider("Age", min_value=12, max_value=90, value=25)
calories = st.sidebar.slider("Calories", min_value=800, max_value=5000, value=2200, step=50)
steps = st.sidebar.slider("Daily Steps", 0, 20000, 8000, help="Check your smartwatch for today's steps")
heart_rate = st.sidebar.slider("Heart Rate (bpm)", 40, 140, 75, help="Use your current or resting heart rate")
sleep_hours = st.sidebar.slider("Sleep Hours", 0, 12, 7, help="Enter last night's sleep duration")

transformer, model = load_artifacts()
features = build_features(age, steps, heart_rate, sleep_hours, calories)
transformed = transform_data(features, transformer)
predicted_calories = float(make_predictions(transformed, model)[0])

activity_score_value = int(features.loc[0, "ActivityScore"])
sleep_score_value = sleep_score(sleep_hours)
calorie_gap = calories - predicted_calories

metric1, metric2, metric3 = st.columns(3)
metric1.metric("Activity Score", f"{activity_score_value}/100")
metric2.metric("Sleep Score", f"{sleep_score_value}/100")
metric3.metric("Predicted Burn", f"{predicted_calories:.0f} kcal", delta=f"{-calorie_gap:.0f} kcal balance")

st.subheader("Recommendations")
for tip in recommendations(activity_score_value, sleep_score_value, calorie_gap):
    st.write(f"- {tip}")
