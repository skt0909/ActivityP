
# Smart Health Recommender

## Overview
This project predicts and visualizes health insights from activity data, including:
- Activity score
- Sleep score
- Predicted calorie burn
- Personalized daily recommendations

The solution consists of:
- **Backend:** Flask API for model inference and recommendations
- **Frontend:** React + Vite dashboard for user interaction
- **Model Training:** Python pipeline for data ingestion, transformation, and model training

---

## Main Features
- Activity, sleep, and calorie predictions
- Personalized recommendations (nutrition, recovery, performance)
- Interactive dashboard (React/Vite frontend)
- Model training pipeline (data ingestion, transformation, training)
- MongoDB integration for data storage

---

## Project Structure

```
ActivityP/
│   main.py                # End-to-end pipeline runner (ingest, transform, train)
│   mongodb.py             # Utility for MongoDB data upload
│   backend/               # Flask API for model inference
│   frontend/              # React + Vite dashboard
│   model/                 # Trained model and transformer artifacts
│   Activity_data/         # Raw activity CSV data
│   Activity_pstructure/   # Core Python package (components, utils, etc.)
│   ...
```

### Key Backend Files
- `backend/app.py` — Flask API for predictions and recommendations
- `Activity_pstructure/utils/inference_utils.py` — Model loading, inference, metrics
- `Activity_pstructure/components/` — Data ingestion, transformation, training

### Key Frontend Files
- `frontend/src/` — React components and main app

---


## Setup Instructions

### 1. Clone the Repository
```sh
git clone <repo-url>
cd ActivityP
```

### 2. Python Environment (Backend & Model Training)
```sh
python -m venv venv
venv\Scripts\activate
python -m pip install -r backend/requirements.txt
```

### 3. Frontend Setup
```sh
cd frontend
npm install
npm run dev
```

### 4. MongoDB Setup (Optional)
Set your MongoDB URI in a `.env` file as `MONGO_DB_URL`.
Use `mongodb.py` to upload CSV data to your MongoDB cluster.

### 5. Model Training
Run the pipeline:
```sh
python main.py
```
Artifacts will be saved in the `model/` folder.

### 6. Start Backend API
```sh
cd backend
python app.py
```
The API will run at `http://localhost:5000`.

---


## API Usage
Send a POST request to `/predict` with user input JSON:

```
{
  "age": 30,
  "gender": "Male",
  "activity_level": "Medium",
  "total_steps": 8000,
  "very_active_minutes": 30,
  "fairly_active_minutes": 20,
  "lightly_active_minutes": 40,
  "sedentary_minutes": 600,
  "sleep_hours": 7.5,
  "calories_intake": 2200
}
```

Response includes predicted calories, scores, and recommendations.

---


## Troubleshooting & Tips

**ModuleNotFoundError: No module named 'Activity_pstructure'**
- Ensure you run scripts from the project root or add the root to `sys.path`.

**FileNotFoundError for model or CSV**
- Make sure `model/model.pkl` and `model/transformer.pkl` exist (run training pipeline if missing).

**MongoDB connection issues**
- Check your `.env` for a valid `MONGO_DB_URL`.

**Frontend not connecting to backend**
- Ensure both backend (`python backend/app.py`) and frontend (`npm run dev` in `frontend/`) are running.

---

## Authors
- Saket Lambe

---

For more details, see code comments and individual module READMEs.
