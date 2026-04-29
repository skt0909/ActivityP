# Predicted Burn Issue - Analysis & Findings

## Problem Statement
**The `predicted_calories` value does NOT change with user input - it stays constant at ~2000 regardless of activity level, age, sleep, etc.**

## Test Results

### Test 1: Low Activity
- Input: age=25, activity_level=Low, sleep=6h, heart_rate=75
- Output: **predicted_calories = 2000**
- Activity Score: 64 ✓ (changes with input)
- Sleep Rating: 81 ✓ (changes with input)

### Test 2: High Activity  
- Input: age=25, activity_level=High, sleep=8h, heart_rate=75
- Output: **predicted_calories = 2000**
- Activity Score: 100 ✓ (changes with input)
- Sleep Rating: 94 ✓ (changes with input)

**Issue**: Other metrics change correctly, but predicted_calories stays at 2000

---

## Root Cause Analysis

### The Prediction Pipeline

The backend has **two stages** of prediction:

1. **Stage 1: ML Model Prediction**
   - Takes engineered features
   - Passes through transformer (StandardScaler + OneHotEncoder)
   - Model predicts raw calorie burn
   - **Result: Always returns ~2000**

2. **Stage 2: Adjustment for Sidebar Inputs** (lines 329 in backend/app.py)
   - Function: `adjust_prediction_for_sidebar_inputs()`
   - Should apply +/- adjustments based on:
     - Age (±3 cal/year deviation)
     - Heart rate (±4 cal/bpm deviation)
     - Sleep hours (±18 cal/hour deviation)
     - Gender (±90 cal adjustment)
     - Activity level (±120 to +180 cal)
     - Active minutes (±2.5 cal/minute)

### Expected vs Actual Output

For Test 2 (High Activity), manual calculation:
```
Raw model prediction: 2000
Adjustments:
  - hr_term (75 bpm):      +20
  - sleep_term (8 hours):  +9
  - age_term (25 years):   +15
  - gender_term (Male):    +90
  - level_term (High):     +180
  - activity_term (156 min): +165
  
Total adjustment: +479
Expected final: 2000 + 479 = 2479 kcal

Actual final: 2000 kcal ❌
```

---

## Issues Identified

### Issue #1: Model Always Predicts ~2000
The scikit-learn model (trained in ModelTrainer) consistently predicts around 2000 regardless of input features. This could mean:
- ✗ The model was trained on data where most samples had ~2000 calorie burn
- ✗ The model is a dummy/placeholder model
- ✗ The transformer is not properly fitting the features
- ✗ The training data was not representative

### Issue #2: Adjustment Function Not Being Called (or Silent Failure)
The `adjust_prediction_for_sidebar_inputs()` function:
- Is defined in the code (line 266)
- Should be called on line 329
- **But returns unchanged 2000 value**

Possible causes:
1. Function raises an exception that's caught silently
2. The print statements (added by me) are not outputting (possible stderr issue)
3. The function is returning 2000 (e.g., all adjustment terms sum to zero)
4. The prediction is being overwritten somewhere after adjustment

---

## Code Evidence

### The Adjustment Function (Works Correctly in Logic)
```python
def adjust_prediction_for_sidebar_inputs(predicted_calories, data, engineered_df):
    # Extracts parameters
    age = float(data.get('age', 30))
    heart_rate = float(data.get('heart_rate', 75))
    sleep_hours = float(data.get('sleep_hours', 7.5))
    gender = str(data.get('gender', 'Male')).strip().lower()
    activity_level = str(data.get('activity_level', 'Medium')).strip().lower()  
    active_minutes = float(engineered_df['ActiveMinutesTotal'].iloc[0])
    
    # Computes adjustment terms
    hr_term = (heart_rate - 70.0) * 4.0
    sleep_term = (sleep_hours - 7.5) * 18.0
    age_term = -(age - 30.0) * 3.0
    gender_term = 90.0 if gender == 'male' else -30.0
    level_term = {'low': -120.0, 'medium': 0.0, 'high': 180.0}.get(activity_level, 0.0)
    activity_term = (active_minutes - 90.0) * 2.5
    
    adjusted = predicted_calories + hr_term + sleep_term + age_term + gender_term + level_term + activity_term
    return max(800.0, adjusted)  # Returns adjusted value
```

The logic is sound, but it's not producing the expected output.

---

## What Needs to Be Investigated

### Priority 1: Debug the Adjustment Function
Add try-except logging to see if it's raising an exception:
```python
try:
    predicted_calories = adjust_prediction_for_sidebar_inputs(predicted_calories, data, X)
except Exception as e:
    print(f"[ERROR] Adjustment failed: {e}")
    # Currently might be failing silently
```

### Priority 2: Check if Model is Viable
The model file (`model.pkl`) needs to be inspected:
- What type of model is it? (LinearRegression, RandomForest, GradientBoosting?)
- Was it trained properly or is it a placeholder?
- What were the training metrics (R² score)?

### Priority 3: Verify Feature Engineering
The features sent to the transformer might not match what it expects:
- Are all 29 feature columns present?
- Are they in the correct order?
- Are any NaN or zero values being created?

---

## Recommended Fixes

### Quick Fix: Make Adjustment Function Mandatory
If the model can't be fixed immediately, make sure the adjustment function at least works:
```python
predicted_calories = adjust_prediction_for_sidebar_inputs(2000, data, X)
# This should at least give variable output even if model always returns 2000
```

### Long-Term Fix: Retrain the Model
Run `main.py` with fresh training data:
```bash
python main.py
```
This will:
1. Ingest data from MongoDB
2. Transform and preprocess
3. Train LinearRegression, RandomForest, GradientBoosting
4. Select the best model
5. Save to `model/model.pkl`

### Deployment Impact
**The predicted_calories is currently non-functional**. It should NOT be used for:
- Calorie deficit/surplus calculations
- Diet recommendations based on burn rate
- Any health metrics that depend on accurate energy expenditure

The `activity_score` and `sleep_quality_rating` ARE working correctly and can be trusted.

---

##Next Steps

1. **Check the backend logs** for any exceptions when `/predict` is called
2. **Inspect model.pkl** to see if it's a real trained model or a placeholder
3. **Retrain the model** using `python main.py` if needed
4. **Add error handling** to the adjustment function so failures are visible
5. **Test with actual data** from the training set to verify model behavior
