# Model Loading Issue - Root Cause Analysis

## **The Problem is NOT the Model Logic**

The model (`model.pkl`) **cannot be loaded due to a scikit-learn version mismatch**.

## **The Evidence**

### Startup Logs
```
[startup] ERROR loading model: Can't get attribute '__pyx_unpickle_CyHalfSquaredError' 
on <module 'sklearn._loss._loss' from '...sklearn\_loss\_loss.cp313-win_amd64.pyd'>
```

### Version Mismatch
```
Trained with:  scikit-learn 1.5.2
Installed:     scikit-learn 1.6.1
```

### Warnings
```
InconsistentVersionWarning: Trying to unpickle estimator StandardScaler from version 1.5.2 
when using version 1.6.1. This might lead to breaking code or invalid results.
```

---

## **Why `predicted_calories=2000` Despite Model Error?**

1. **Model fails to load** → `model = None`
2. **Transformer loads successfully** → `transformer = not None`
3. **Code checks if model is None** → Should return 503 error
4. **BUT API returns 200 OK with predictions** → Something is creating predictions anyway

**Possible explanation**: 
- Error handling is silently catching the exception and using a fallback
- Or a DummyModel is being created as fallback
- Or there's a try-except that allows execution to continue with None model

---

## **Why Is This a Problem for Deployment?**

When you deploy to production (e.g., Render, Railway):
1. scikit-learn might be upgraded to 1.6.1 or newer
2. The old `model.pkl` (trained with 1.5.2) will fail to load
3. The prediction system will either crash or use a fallback/dummy model
4. **predicted_calories will be unreliable or constant**

---

## **The Fix: Retrain the Model**

You must retrain the model with the current scikit-learn version:

```bash
# This will:
# 1. Fetch data from MongoDB
# 2. Transform and preprocess
# 3. Train RandomForest, GradientBoosting, LinearRegression
# 4. Save new model.pkl (compatible with scikit-learn 1.6.1)
python main.py
```

### What This Does
- Creates a new `model/model.pkl` compatible with scikit-learn 1.6.1
- Creates a new `model/transformer.pkl` compatible with scikit-learn 1.6.1
- Ensures the model loads without errors in production

---

## **Immediate Actions Required**

### 1. **Retrain the Model** (Required for deployment)
```bash
python main.py
```

### 2. **Verify the Model Loads** (After retraining)
```bash
python backend/app.py
# Should see:
# [startup] Model loaded successfully ✅
# NOT:
# [startup] ERROR loading model: ❌
```

### 3. **Test Predictions Work**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"age":25,"gender":"Male",...}'

# Check that predicted_calories varies with activity level
# NOT constant 2000
```

---

## **Why predicted_calories Is Currently 2000**

After model retraining, if `predicted_calories` is STILL 2000 for all inputs, then:
1. The trained model genuinely predicts ~2000 for all features (mean prediction)
2. The **adjustment function** in `adjust_prediction_for_sidebar_inputs()` is responsible for creating variation
3. That adjustment function must be debugged next

But first: **retrain the model**.

---

## **For Deployment**

- Add to your deployment pipeline:
  ```bash
  # Before starting the app
  python main.py  # Retrain model with current scikit-learn
  ```
- Or commit the newly trained `model/model.pkl` and `model/transformer.pkl` to git
- Ensure `requirements.txt` pins scikit-learn to a specific version in the future

---

## **Summary**

| Issue | Root Cause | Status |
|-------|-----------|--------|
| Model fails to load | scikit-learn 1.5.2 → 1.6.1 mismatch | **FIXABLE - Retrain model** |
| predicted_calories=2000 | Model loading fails silently | Will resolve after retraining |
| Adjustment function not working | Still unknown | Debug after model fix |
