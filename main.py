import os
from pymongo.mongo_client  import MongoClient
from logging import getLogger
from Activity_pstructure.logging.logger import logger
from Activity_pstructure.entity.config_entity import MongoDBConfig
from Activity_pstructure.constant.database import DATABASE_NAME, COLLECTION_NAME
from Activity_pstructure.components.ingestion import DataIngestion

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
