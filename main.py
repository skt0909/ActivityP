import os
import pandas as pd 
from pymongo.mongo_client  import MongoClient
from logging import getLogger
from Activity_pstructure.logging.logger import logger
from Activity_pstructure.entity.config_entity import MongoDBConfig
from Activity_pstructure.constant.database import DATABASE_NAME, COLLECTION_NAME, PREPROCESSED_DATA_PATH
from Activity_pstructure.components.ingestion import DataIngestion
from Activity_pstructure.components.transformation import transform_and_save_data
from Activity_pstructure.components.model_trainer import ModelTrainer
from Activity_pstructure.entity.config_entity import ModelTrainerConfig
from Activity_pstructure.constant.database import(
    BEST_MODEL_PATH,
    X_TEST_PATH,
    X_TRAIN_PATH,
    Y_TEST_PATH,
    Y_TRAIN_PATH
)

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

if __name__ == "__main__":
    
    config = MongoDBConfig(
        mongo_url= MONGO_DB_URL,
        database_name= DATABASE_NAME,
        collection_name= COLLECTION_NAME
    ) 

    try:
        ingestion = DataIngestion(config)
        df = ingestion.fetch_data_from_mongodb()
        ingestion.save_dataframe_to_artifacts(
            df,
            output_dir=config.output_dir,
            output_filename=config.output_filename
        )
        print("Data ingestion complete.")

    except Exception as e:
        print(f"An error occurred during ingestion: {e}")

    try:
        df = pd.read_csv(PREPROCESSED_DATA_PATH)
        artifact = transform_and_save_data(df, target_column="Calories")
        print("Data transformation complete.")

    except Exception as e:
        print(f"Error during transformation: {e}")

    try:
    
        trainer_config = ModelTrainerConfig(
            X_train_path=X_TRAIN_PATH,
            X_test_path=X_TEST_PATH,
            y_train_path=Y_TRAIN_PATH,
            y_test_path=Y_TEST_PATH,
            model_save_path=BEST_MODEL_PATH
        )

        trainer = ModelTrainer(trainer_config)
        trainer_artifact = trainer.train_and_select_model()
        print(f"Model training complete. Best model: {trainer_artifact.best_model_name}")

    except Exception as e:
        print(f"Error during model training: {e}")


