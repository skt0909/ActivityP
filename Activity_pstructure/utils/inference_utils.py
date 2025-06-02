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

def calculate_custom_metrics(df):
    required_cols = ["ActiveMinutesTotal", "Calories", "SedentaryMinutes"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}'")

    ActivityScore = (df["ActiveMinutesTotal"] / 150).clip(upper=1)
    df["ActivityScore"] = (ActivityScore * 99 + 1).round().astype(int)  

    df["diet_completion"] = df["Calories"].apply(
        lambda x: 100 if x >= 2500 else max(0, (x - 2000) / 500 * 100)
    ).round(2)

    sleep_score = (df["SedentaryMinutes"] / 600).clip(upper=1)
    df["sleep_quality_rating"] = (sleep_score * 9 + 1).round().astype(int)

    return df