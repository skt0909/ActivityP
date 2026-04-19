# Smart Health Recommender - Quick Documentation

## Overview
This project predicts and visualizes health insights from activity data:
- Activity score
- Sleep score
- Predicted calorie burn
- Personalized daily recommendations

The dashboard is built with Streamlit and uses trained artifacts from the `model/` folder.

## Model Input Features
The dashboard constructs inference input using the following exact feature set (`MODEL_FEATURES`):
- `TotalSteps`
- `TotalDistance`
- `TrackerDistance`
- `VeryActiveDistance`
- `ModeratelyActiveDistance`
- `LightActiveDistance`
- `SedentaryActiveDistance`
- `VeryActiveMinutes`
- `FairlyActiveMinutes`
- `LightlyActiveMinutes`
- `SedentaryMinutes`
- `StepsPerMinute`
- `DistancePerStep`
- `VeryActiveRatio`
- `SedentaryRatio`
- `ActiveMinutesTotal`
- `ActivityScore`
- `EffectiveActiveTime`
- `ActivityLevel`
- `Gender`
- `Age`
- `VeryActiveDistance_norm`
- `ModeratelyActiveDistance_norm`
- `SedentaryActiveDistance_norm`
- `VeryActiveMinutes_norm`
- `FairlyActiveMinutes_norm`
- `StepsPerMinute_norm`
- `DistancePerStep_norm`
- `VeryActiveRatio_norm`

## Project Layout
- `Activity_pstructure/app/dashboard.py` - Streamlit dashboard entrypoint
- `Activity_pstructure/utils/inference_utils.py` - inference helper functions
- `Activity_pstructure/components/` - ingestion, transformation, training components
- `model/model.pkl` - trained model artifact
- `model/transformer.pkl` - trained transformer artifact
- `requirements.txt` - Python dependencies

## Environment Setup (Windows CMD)
1. Go to project root:
```cmd
cd /d D:\Proj\ActivityP
```
2. Activate virtual environment:
```cmd
venv\Scripts\activate
```
3. Install dependencies:
```cmd
python -m pip install -r requirements.txt
```

## Run Dashboard
Use module mode (recommended):
```cmd
cd /d D:\Proj\ActivityP\Activity_pstructure\app
python -m streamlit run dashboard.py
```

If venv is not activated:
```cmd
cd /d D:\Proj\ActivityP\Activity_pstructure\app
D:\Proj\ActivityP\venv\python.exe -m streamlit run dashboard.py
```

Default URL:
- `http://localhost:8501`

## Known CLI Issue and Fix
### Symptom
`streamlit run dashboard.py` fails with launcher path error.

### Cause
`venv\Scripts\streamlit.exe` may point to an outdated Python path.

### Workarounds
1. Run Streamlit with Python module:
```cmd
python -m streamlit run dashboard.py
```
2. Rebuild Streamlit launcher:
```cmd
python -m pip install --force-reinstall streamlit
```

## Common Errors
### `ModuleNotFoundError: No module named 'Activity_pstructure'`
- Fixed in dashboard by adding project root to `sys.path`.
- Ensure you run from:
  - `D:\Proj\ActivityP\Activity_pstructure\app`

### `FileNotFoundError` for CSV/model paths
- Ensure these files exist:
  - `D:\Proj\ActivityP\model\transformer.pkl`
  - `D:\Proj\ActivityP\model\model.pkl`

## Notes for Development
- Keep imports package-based (`Activity_pstructure...`) for consistency.
- Prefer relative path construction using `pathlib.Path` instead of hardcoded absolute strings.
- After code changes, quick sanity check:
```cmd
python -m py_compile Activity_pstructure\app\dashboard.py
```
