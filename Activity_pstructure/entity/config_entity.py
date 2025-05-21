from dataclasses import dataclass

@dataclass
class MongoDBConfig:
    mongo_url: str
    database_name: str
    collection_name: str
    output_dir: str = "artifacts"
    output_filename: str = "activity_data.csv"

@dataclass
class DataTransformationArtifact:
    X_train_path: str
    X_test_path: str
    y_train_path: str
    y_test_path: str
    transformer_path: str  