import os
import sys
import pandas as pd 
import numpy as np
import pickle
from Activity_pstructure.constant.database import X_TEST_PATH, X_TRAIN_PATH, Y_TEST_PATH, Y_TRAIN_PATH, TRANSFORMER_PATH
from Activity_pstructure.entity.config_entity import DataTransformationArtifact
from Activity_pstructure.utils.common_utils import save_object
from Activity_pstructure.logging.logger import logger
from Activity_pstructure.exception.exception import ActivityException

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def transform_and_save_data(df: pd.DataFrame, target_column: str) -> DataTransformationArtifact:
    try:
        logger.info("Starting transformation pipeline")

        # Drop the leakage column
        if 'Calories_norm' in df.columns:
            df.drop(columns=['Calories_norm'], inplace=True)
            logger.info("Dropped 'Calories_norm")

        # Separate features and target
        X = df.drop(columns=[target_column])
        y = df[target_column]

        logger.info(f"Splitting dataset into train and test")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Define column types manually
        numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_cols = ['Gender']
        ordinal_cols = ['ActivityLevel']

        # Remove 'Gender' and 'ActivityLevel' from numerical
        for col in categorical_cols + ordinal_cols:
            if col in numerical_cols:
                numerical_cols.remove(col)

        logger.info(f" Numerical: {numerical_cols}")
        logger.info(f" One-hot: {categorical_cols}")
        logger.info(f"Ordinal: {ordinal_cols}")

        # Define transformers
        numeric_transformer = Pipeline(steps=[
            ("scaler", StandardScaler())
        ])

        categorical_transformer = Pipeline(steps=[
            ("onehot", OneHotEncoder(drop="first", sparse_output=False))
        ])

        ordinal_transformer = Pipeline(steps=[
            ("ordinal", OrdinalEncoder(categories=[["Low", "Medium", "High"]]))
        ])

        preprocessor = ColumnTransformer(transformers=[
            ("num", numeric_transformer, numerical_cols),
            ("cat", categorical_transformer, categorical_cols),
            ("ord", ordinal_transformer, ordinal_cols)
        ])

        logger.info("Fitting transformer on training data")
        X_train_transformed = preprocessor.fit_transform(X_train)
        X_test_transformed = preprocessor.transform(X_test)

        # Save transformed arrays and labels
        logger.info("Saving transformed datasets and pipeline")
        save_object(X_train_transformed, X_TRAIN_PATH)
        save_object(X_test_transformed, X_TEST_PATH)
        save_object(y_train, Y_TRAIN_PATH)
        save_object(y_test, Y_TEST_PATH)
        save_object(preprocessor, TRANSFORMER_PATH)

        logger.info("Data transformation complete and saved.")

        return DataTransformationArtifact(
            X_train_path=X_TRAIN_PATH,
            X_test_path=X_TEST_PATH,
            y_train_path=Y_TRAIN_PATH,
            y_test_path=Y_TEST_PATH,
            transformer_path=TRANSFORMER_PATH
        )
    except Exception as e:
        raise ActivityException(e, sys)
