# inference/utils.py
import pandas as pd
import joblib


def load_csv(path):
    return pd.read_csv(path)


def load_transformer(path):
    return joblib.load(path)


def load_model(path):
    return joblib.load(path)


def transform_data(df, transformer):
    return transformer.transform(df)


def make_predictions(X, model):
    return model.predict(X)


def calculate_custom_metrics(df, sleep_hours=None, calories_intake=None):
    """
    Compute display metrics from the engineered feature DataFrame.

    Parameters
    ----------
    df              : engineered feature DataFrame (post-transform copy with 'Calories')
    sleep_hours     : raw user input (float, hours slept)
    calories_intake : raw user input (int, calories consumed today)

    Metrics
    -------
    ActivityScore        — 1-100  based on WHO 150-min/week active-minutes guideline
    sleep_quality_rating — 1-100  based on proximity to the 7.5 h optimal sleep target
    diet_completion      — ratio  calories_intake / predicted_burn  (1.0 = perfect balance)
    """
    required_cols = ["ActiveMinutesTotal", "Calories"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}'")

    # ── Activity Score ─────────────────────────────────────────────────────────
    # Realistic daily targets (aligned with sidebar activity_level baselines):
    #   Low    ≈  4 000 steps / 85 spm ≈  47 min  →  ~52 %
    #   Medium ≈  8 000 steps / 85 spm ≈  94 min  →  ~100% (target ceiling)
    #   High   ≈ 13 000 steps / 85 spm ≈ 153 min  →  100%  (capped)
    # Target ceiling = 90 min/day (WHO 150 min/week ÷ ~1.67 active days).
    activity_ratio = (df["ActiveMinutesTotal"] / 90.0).clip(upper=1.0)
    df["ActivityScore"] = (activity_ratio * 99 + 1).round().astype(int)

    # ── Sleep Quality Rating ───────────────────────────────────────────────────
    # Optimal sleep = 7.5 h.  Each hour away from optimal costs ~12.5 points.
    # Score = 100 - |sleep_hours - 7.5| * 12.5, clamped to [1, 100].
    if sleep_hours is not None:
        deviation = abs(float(sleep_hours) - 7.5)
        sleep_score = max(1.0, 100.0 - deviation * 12.5)
    else:
        # Fallback: estimate from SedentaryMinutes if sleep_hours not provided.
        # Assume ~8 h ideal sleep = 480 min sedentary at night.
        sedentary = df.get("SedentaryMinutes", pd.Series([480]))
        est_sleep_hours = sedentary.iloc[0] / 60.0 * 0.4  # crude proxy
        deviation = abs(est_sleep_hours - 7.5)
        sleep_score = max(1.0, 100.0 - deviation * 12.5)

    df["sleep_quality_rating"] = int(round(min(100.0, sleep_score)))

    # ── Diet Completion ────────────────────────────────────────────────────────
    # Ratio of calories consumed to predicted burn.
    # 1.0 = perfect balance, >1 = surplus, <1 = deficit.
    if calories_intake is not None:
        diet_completion = float(calories_intake) / max(float(df["Calories"].iloc[0]), 1.0)
    else:
        # If no intake provided, assume balanced
        diet_completion = 1.0

    df["diet_completion"] = round(diet_completion, 3)

    return df