import pandas as pd
import sys
import os
from pymongo.mongo_client import MongoClient
from logging import getLogger
from Activity_pstructure.logging.logger import logger
from Activity_pstructure.exception.exception import ActivityException
from Activity_pstructure.entity.config_entity import MongoDBConfig

logger = getLogger("activity_logger")

class DataIngestion:
    def __init__(self, config: MongoDBConfig):
        self.config = config

    def fetch_data_from_mongodb(self) -> pd.DataFrame:
        try:
            logger.info("Starting data retrieval from MongoDB Atlas...")

            client = MongoClient(self.config.mongo_url)
            db = client[self.config.database_name]
            collection = db[self.config.collection_name]

            cursor = collection.find()
            data = list(cursor)

            for doc in data:  # Remove _id field if present
                doc.pop('_id', None)

            df = pd.DataFrame(data)
            logger.info(f"Retrieved {len(df)} records from MongoDB.")
            return df

        except Exception as e:
            raise ActivityException(e, sys)

    def save_dataframe_to_artifacts(self, df: pd.DataFrame, output_dir: str, output_filename: str):
        try:
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, output_filename)

            df.to_csv(file_path, index=False)
            logger.info(f"DataFrame saved to {file_path}")

        except Exception as e:
            logger.error(f"Failed to save DataFrame: {e}")
            raise ActivityException(e, sys)
    
 
