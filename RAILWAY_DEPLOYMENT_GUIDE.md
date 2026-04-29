# Railway Deployment Guide - Handling Version Conflicts

## **Problem You're Solving**

When deploying to Railway:
- ❌ scikit-learn might upgrade from 1.5.2 to 1.6.1
- ❌ Model pickle file becomes incompatible
- ❌ Deployment fails or predictions break

## **Solutions (In Order of Preference)**

### **Solution 1: Use Docker (RECOMMENDED) ✅**

This is the **safest method** because:
- Uses exact Python version (3.13.3)
- Pins exact scikit-learn (1.5.2)
- Reproducible across all environments
- Works on Railway, AWS, GCP, local, etc.

**Steps:**

1. **Files already created:**
   - ✅ `Dockerfile` - Specifies Python 3.13.3 + pinned dependencies
   - ✅ `railway.json` - Railway deployment config
   - ✅ `backend/requirements.txt` - All dependencies pinned to exact versions

2. **Deploy to Railway:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Initialize project
   railway init
   
   # Deploy
   railway up
   ```

3. **Railway will automatically:**
   - Detect `Dockerfile`
   - Build with exact Python 3.13.3
   - Install exact scikit-learn 1.5.2
   - Start with gunicorn

---

### **Solution 2: Use Procfile + Environment Variables**

If you don't want to use Docker, at least enforce versions on Railway:

1. **Procfile** (already created):
   ```
   web: gunicorn --bind 0.0.0.0:$PORT --workers 4 backend.app:app
   ```

2. **Set Railway environment variables:**
   - Go to: Railway Dashboard → Your Project → Variables
   - Add: `PYTHON_VERSION=3.13.3`
   - Add: `PIP_COMPILE_ALL_DEPS=true`

3. **Railway will use:**
   - Python 3.13.3 (exactly)
   - `requirements.txt` with pinned versions

---

### **Solution 3: requirements.txt Only (Works But Less Reliable)**

Just ensure `backend/requirements.txt` has exact versions:

```txt
scikit-learn==1.5.2
numpy==1.26.4
pandas==2.2.0
# ... all with == not >=
```

**Why this is risky:**
- Python version might vary (3.13.2 vs 3.13.3)
- System packages might differ
- Some C-extension libraries might mismatch

---

## **What's Different Now?**

| Before | Now |
|--------|-----|
| `scikit-learn` (any version) | `scikit-learn==1.5.2` ✅ |
| No Python version specified | `Python 3.13.3` in Dockerfile ✅ |
| `requirements.txt` incomplete | All 20+ dependencies pinned ✅ |
| No Docker | `Dockerfile` provided ✅ |
| No Railway config | `railway.json` provided ✅ |

---

## **Deployment Checklist**

- [ ] Model retrained with scikit-learn 1.5.2 (`python main.py`)
- [ ] `backend/requirements.txt` has exact versions
- [ ] `Dockerfile` created
- [ ] `railway.json` created
- [ ] `Procfile` created
- [ ] Frontend `VITE_API_URL` env var set to Railway backend URL
- [ ] MongoDB `MONGO_DB_URL` env var set in Railway
- [ ] Test locally: `docker build -t activity-p . && docker run -p 5000:5000 activity-p`
- [ ] Deploy to Railway: `railway up`

---

## **How to Deploy on Railway**

### **Using Docker (Recommended)**

```bash
cd /path/to/ActivityP

# Login to Railway
railway login

# Initialize (if first time)
railway init

# Check status
railway status

# View logs
railway logs

# Deploy
railway up
```

### **Railway Will:**
1. Detect `Dockerfile`
2. Build image with Python 3.13.3
3. Run `pip install -r backend/requirements.txt`
4. Start with command in `railway.json`
5. Expose on public URL

### **Set Environment Variables on Railway:**

Go to: **Project Settings → Variables**

```
FLASK_ENV=production
PORT=5000
ALLOWED_ORIGINS=https://your-frontend-url.com
MONGO_DB_URL=mongodb+srv://user:pass@cluster.mongodb.net/SKT
```

---

## **After Deployment**

1. **Test the API:**
   ```bash
   curl -X POST https://your-railway-app.up.railway.app/predict \
     -H "Content-Type: application/json" \
     -d '{"age":25,"gender":"Male",...}'
   ```

2. **Update Frontend:**
   Set `VITE_API_URL` to your Railway backend URL:
   ```
   VITE_API_URL=https://your-railway-app.up.railway.app
   ```

3. **Check Logs:**
   ```bash
   railway logs
   # Should see:
   # [startup] Model loaded successfully ✅
   # NOT: [startup] ERROR loading model ❌
   ```

---

## **Troubleshooting**

### **Error: Can't get attribute '__pyx_unpickle_CyHalfSquaredError'**
- Model was trained with different scikit-learn version
- **Fix:** Retrain: `python main.py`

### **Port Issues**
- Make sure `PORT` env var is used: `port = int(os.environ.get('PORT', 5000))`
- Already fixed in `backend/app.py` ✅

### **CORS Issues**
- Update `ALLOWED_ORIGINS` env var on Railway
- Or update in `backend/app.py` line 26

### **Model Not Loading**
- Check logs: `railway logs`
- Verify scikit-learn version matches
- Restart: `railway down && railway up`

---

## **Docker Testing (Before Deploying)**

Test locally that Docker build works:

```bash
cd d:/Proj/ActivityP

# Build image
docker build -t activity-p:latest .

# Run container
docker run -p 5000:5000 \
  -e MONGO_DB_URL="mongodb+srv://..." \
  -e ALLOWED_ORIGINS="http://localhost:3000" \
  activity-p:latest

# Test API
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"age":25,...}'
```

If this works locally, it will work on Railway.

---

## **Future: Preventing This Again**

For next deployment:
1. **Always pin scikit-learn** to match training environment
2. **Use Docker** for reproducibility
3. **Test Docker image locally** before pushing to Railway
4. **Pin Python version** (3.13.3)
5. **Use `pip freeze`** to generate exact requirements after development

---

## **Summary**

✅ **Already Done:**
- Pinned all dependencies in `backend/requirements.txt`
- Created `Dockerfile` with Python 3.13.3
- Created `railway.json` with deployment config
- Created `Procfile` as fallback

✅ **Next Steps:**
1. Retrain model: `python main.py`
2. Test locally: `docker build && docker run`
3. Deploy: `railway up`
4. Set Railway env vars
5. Update frontend API URL

**Result:** No more version conflicts on Railway! 🚀
