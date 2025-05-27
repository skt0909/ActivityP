import pandas as pd
import sys
import os
from datetime import datetime
from pymongo.mongo_client import MongoClient
from logging import getLogger
from Activity_pstructure.logging.logger import logger
from Activity_pstructure.exception.exception import ActivityException
from Activity_pstructure.entity.config_entity import MongoDBConfig
from Activity_pstructure.utils.common_utils import save_dataframe
from Activity_pstructure.entity.config_entity import MongoDBArtifact

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
        save_dataframe(df, output_dir, output_filename, logger=logger)

    def initiate_data_ingestion(self) -> MongoDBArtifact:
        try:
            df = self.fetch_data_from_mongodb()
            file_path = self.save_dataframe_to_artifacts(df, self.config.output_dir, self.config.output_filename)

            artifact = MongoDBArtifact(
                output_file_path=file_path,
                record_count=len(df),
                extraction_timestamp=datetime.now().isoformat()
            )
            logger.info(f"MongoDB ingestion completed. Artifact: {artifact}")
            return artifact

        except Exception as e:
            raise ActivityException(e, sys)
 
