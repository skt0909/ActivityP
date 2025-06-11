from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import joblib

INPUT_PATH = '/opt/airflow/include/data/testdata2.csv'
TRANSFORMER_PATH = '/opt/airflow/include/model/transformer.pkl'
MODEL_PATH = '/opt/airflow/include/model/model.pkl'

# Use global variable to pass data across tasks (simplified for local runs)
global_df = {}

# Functions
def load_data(**context):
    df = pd.read_csv(INPUT_PATH)
    global_df['df'] = df

def transform_data(**context):
    df = global_df['df']
    transformer = joblib.load(TRANSFORMER_PATH)
    X = transformer.transform(df)
    global_df['X'] = X

def predict(**context):
    X = global_df['X']
    model = joblib.load(MODEL_PATH)
    preds = model.predict(X)
    global_df['preds'] = preds


# DAG definition
with DAG(
    dag_id='ml_prediction_pipeline',
    start_date=datetime(2025, 6, 1),
    schedule_interval=None,
    catchup=False,
    tags=['ml', 'local']
) as dag:

    t1 = PythonOperator(
        task_id='load_csv',
        python_callable=load_data
    )

    t2 = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data
    )

    t3 = PythonOperator(
        task_id='predict',
        python_callable=predict
    )



    t1 >> t2 >> t3 
