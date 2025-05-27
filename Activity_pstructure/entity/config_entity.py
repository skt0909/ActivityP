from dataclasses import dataclass
from typing import List

@dataclass
class MongoDBArtifact:
    output_file_path: str
    record_count: int
    extraction_timestamp: str

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


@dataclass
class ModelTrainerConfig:
    X_train_path: str
    X_test_path: str
    y_train_path: str
    y_test_path: str
    model_save_path: str  # Final best model .pkl path

@dataclass
class ModelTrainerArtifact:
    model_path: str
    train_score: float
    test_score: float
    best_model_name: str