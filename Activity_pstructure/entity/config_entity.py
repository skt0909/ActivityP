from dataclasses import dataclass

@dataclass
class MongoDBConfig:
    mongo_url: str
    database_name: str
    collection_name: str
    output_dir: str = "artifacts"
    output_filename: str = "activity_data.csv"