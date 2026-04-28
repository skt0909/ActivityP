# Deploying to Railway

This guide explains how to deploy the ActivityP fullstack app to Railway using Docker.

## Prerequisites

1. Railway account: https://railway.app
2. GitHub account with this repo pushed
3. Docker installed locally (for testing)

## Architecture

- **Backend**: Flask API running in Docker on Railway (this repo's Dockerfile)
- **Frontend**: React/Vite deployed separately to Vercel, Netlify, or Railway
- **Database**: MongoDB Atlas (cloud-hosted, no changes needed)

---

## Step 1: Test Locally with Docker

Before deploying, test the Docker setup locally:

```bash
# Build and run with docker-compose
docker-compose up

# In another terminal, test the API
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 25,
    "gender": "Male",
    "activity_level": "Moderately Active",
    "total_steps": 8000,
    "very_active_minutes": 30,
    "fairly_active_minutes": 20,
    "lightly_active_minutes": 60,
    "sedentary_minutes": 400,
    "sleep_hours": 7,
    "calories_intake": 2000
  }'
```

---

## Step 2: Push to GitHub

Make sure your repo is on GitHub with all changes committed:

```bash
git add .
git commit -m "Add Docker config and CORS/rate limiting for Railway deployment"
git push origin main
```

---

## Step 3: Deploy Backend to Railway

### 3a. Connect Railway to GitHub

1. Go to https://railway.app/dashboard
2. Click **New Project**
3. Select **Deploy from GitHub repo**
4. Authorize GitHub and select your repo
5. Railway will auto-detect the Dockerfile

### 3b. Configure Environment Variables

In the Railway project settings, add these environment variables:

```
ALLOWED_ORIGINS=https://your-frontend-url.com
PORT=5000  (optional, Railway sets this automatically)
```

If you want to run the ML training pipeline on Railway, also add:
```
MONGO_DB_URL=mongodb+srv://<username>:<password>@cluster.mongodb.net/SKT
```

### 3c. Deploy

Railway will automatically build and deploy when you push to GitHub. Check the logs to confirm the backend is running.

Your backend URL will be something like: `https://myapp-production.up.railway.app`

---

## Step 4: Update Frontend with Backend URL

Once your Railway backend is live, update your frontend environment:

**For Vercel/Netlify deployment:**
- Set environment variable: `VITE_API_URL=https://your-railway-backend-url.com`
- Redeploy frontend

**For local development:**
- Update `frontend/.env.local`: `VITE_API_URL=https://your-railway-backend-url.com`
- Run `npm run dev`

---

## Step 5: Deploy Frontend

Deploy to Vercel, Netlify, or Railway. Make sure to set the `VITE_API_URL` environment variable pointing to your Railway backend.

---

## Security & Features

### CORS (Cross-Origin Resource Sharing)
- **Restricted**: Only your frontend origin can call the API
- **Configurable**: Set via `ALLOWED_ORIGINS` env var
- Multiple origins supported (comma-separated): `https://frontend1.com,https://frontend2.com`

### Rate Limiting
- **100 requests per hour** per IP address
- Prevents abuse of the `/predict` endpoint
- Adjust in `backend/app.py` if needed

### Production Settings
- Flask debug mode is OFF
- Using Gunicorn (production-grade WSGI server) with 4 workers
- Timeout set to 120 seconds for long-running predictions

---

## Troubleshooting

### Backend won't start
Check Railway logs for errors. Common issues:
- Missing dependencies: ensure `backend/requirements.txt` is complete
- Model files not found: check that `model/model.pkl` and `model/transformer.pkl` exist

### CORS errors in browser
- Check `ALLOWED_ORIGINS` env var matches your frontend URL exactly
- Include protocol (https://) and exclude trailing slashes

### Rate limit errors
If you hit "429 Too Many Requests", the frontend is calling the API more than 100 times per hour. Either:
- Increase the limit in `backend/app.py` line ~25
- Optimize frontend to make fewer requests
- Use caching on the frontend

---

## Monitoring

Railroad provides logs and metrics in the dashboard. Monitor:
- **Response times**: should be < 2 seconds for `/predict`
- **Error rates**: check for 5xx errors in logs
- **Memory/CPU**: should be low for a lightweight Flask app

---

## Next Steps

After successful deployment:
1. Test the full flow: frontend → API → prediction
2. Verify CORS is working (no "blocked by CORS" errors)
3. Monitor logs for 48 hours after deployment
4. Set up error alerts if available
