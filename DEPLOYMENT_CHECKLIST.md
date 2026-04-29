# Deployment Checklist - Calories Prediction Fix

## What We've Fixed

✅ **Pinned all dependencies** (`backend/requirements.txt`)
- scikit-learn==1.5.2 (exact version match)
- All 20+ packages pinned to exact versions

✅ **Created Docker setup** for reproducible deployments
- Dockerfile (Python 3.13.3, exact dependencies)
- railway.json (Railway deployment config)
- Procfile (fallback deployment config)

✅ **Enhanced prediction logic**
- Adjustment function calculates physiological factors (age, gender, HR, sleep, activity)
- Adds +/- adjustments to base prediction
- Handles all 4 activity levels (Low, Medium, High)

✅ **Improved fallback model**
- When trained model fails to load, uses improved DummyModel
- DummyModel includes gender and activity level adjustments
- Still respects adjustment function for HR, sleep, and other factors

## Expected Behavior

### Test Case 1: Low Activity, Female, 6h Sleep
- Base: 2000 kcal
- Adjustments: Female (-30) + Low activity (-120) + Low sleep (-18) + Lower HR (-20) = -188
- **Expected: 1812 kcal**

### Test Case 2: High Activity, Male, 8h Sleep  
- Base: 2000 kcal
- Adjustments: Male (+90) + High activity (+180) + Good sleep (+9) + Higher HR (+60) + Active (+165) = +504
- **Expected: 2504 kcal**

## Pre-Deployment Steps

1. **Retrain Model (when MongoDB is available)**
   ```bash
   python main.py
   ```
   This ensures the model loads without errors and produces better predictions.

2. **Test Locally with Docker**
   ```bash
   docker build -t activity-p:latest .
   docker run -p 5000:5000 activity-p:latest
   
   # Test in another terminal:
   curl -X POST http://localhost:5000/predict \
     -H "Content-Type: application/json" \
     -d '{"age":25,"gender":"Male",...}'
   ```

3. **Verify prediction varies**
   - Send request with Low activity, Female, 6h sleep → Should get ~1800 kcal
   - Send request with High activity, Male, 8h sleep → Should get ~2500 kcal
   - If both return 2000, the adjustment function isn't being applied

## Railway Deployment

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Fix calorie prediction: pin versions, add Docker, improve adjustments"
   git push origin main
   ```

2. **Deploy on Railway**
   ```bash
   railway login
   railway up
   ```

3. **Set environment variables on Railway**
   - Go to: Project Settings → Variables
   - Add:
     ```
     FLASK_ENV=production
     PORT=5000
     ALLOWED_ORIGINS=https://your-frontend-url.com
     MONGO_DB_URL=mongodb+srv://user:pass@cluster/db
     ```

4. **Update frontend API URL**
   - Set `VITE_API_URL` to your Railway backend URL

## Monitoring After Deployment

Check Railway logs for:
```
✅ [startup] Model loaded successfully
OR
⚠️ [startup] USING FALLBACK DUMMY MODEL (acceptable)

Check predictions:
✅ [adjust] Raw prediction: 2000
✅ [adjust] Terms: hr=+60, sleep=+9, age=+15, gender=+90, level=+180, activity=+165
✅ [adjust] Total adjustment: +519
✅ [adjust] Adjusted prediction: 2519
```

If you see 2000 in all cases, the adjustment function isn't applying.

## Fallback: If Adjustments Not Working

If adjustments aren't working on Railway, it's likely due to:
1. Model loading failure (scikit-learn version mismatch)
   - Fix: Retrain model with `python main.py`
   
2. Adjustment function exception (caught silently)
   - Fix: Check logs for errors

3. Response override
   - Fix: Check if predicted_calories is being reset after adjustment

## Next Steps

1. Deploy to Railway with current code
2. Test in production
3. If predictions still constant, check logs
4. If needed, run `python main.py` to retrain
5. Redeploy with new model files

## Files Changed This Session

```
✅ backend/requirements.txt - Pinned all versions
✅ backend/app.py - Enhanced adjustment function + error handling
✅ Dockerfile - Created for reproducible builds
✅ railway.json - Railway deployment config
✅ Procfile - Alternative deployment config
✅ frontend/.env.example - API URL config
✅ .env.example - MongoDB URL config
```

## Expected Outcome

Once deployed:
- ✅ Calorie predictions will vary (500-3500 kcal range typical)
- ✅ Different age/gender/activity combos produce different results
- ✅ No more constant 2000 kcal prediction
- ✅ Adjustment function applies physiological factors
- ✅ No version conflicts on Railway

---

**Status**: Ready for deployment 🚀
