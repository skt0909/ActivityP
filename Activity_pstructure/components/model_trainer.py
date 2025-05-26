import pandas as pd
import numpy as np
import pickle
import os
import sys

from Activity_pstructure.entity.config_entity import ModelTrainerArtifact, ModelTrainerConfig
from Activity_pstructure.utils.common_utils import load_object, save_object
from Activity_pstructure.logging.logger import logger
from Activity_pstructure.exception.exception import ActivityException

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import mlflow
from mlflow.models.signature import infer_signature
import dagshub

dagshub.init(repo_owner='skt0909', repo_name='ActivityP', mlflow=True)



class ModelTrainer:
    def __init__(self, config: ModelTrainerConfig):
        self.config = config

    def track_mlflow(self, model, metrics, model_name, X_test):
        try:
            with mlflow.start_run(run_name=model_name):
                mlflow.log_param("model_name", model_name)

                # Log all regression metrics
                mlflow.log_metric("train_r2", metrics.get("train_r2", None))
                mlflow.log_metric("test_r2", metrics.get("test_r2", None))
                mlflow.log_metric("rmse", metrics.get("rmse", None))
                mlflow.log_metric("mae", metrics.get("mae", None))

                  # Infer signature and log model with input example
                signature = infer_signature(X_test, model.predict(X_test))
                input_example = X_test[:5]

                mlflow.sklearn.log_model(
                    sk_model=model,
                    artifact_path="model",
                    signature=signature,
                    input_example=input_example
                )
        except Exception as e:
            logger.error(f"MLflow tracking failed for {model_name}: {e}")


    def _evaluate_model(self, model, X_train, y_train, X_test, y_test):
        model.fit(X_train, y_train)
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        return {
            "model": model,
            "train_r2": r2_score(y_train, y_train_pred),
            "test_r2": r2_score(y_test, y_test_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_test_pred)),
            "mae": mean_absolute_error(y_test, y_test_pred)
        }

    def _tune_model(self, model, param_grid, X_train, y_train):
        search = RandomizedSearchCV(
            estimator=model,
            param_distributions=param_grid,
            n_iter=10,
            scoring="r2",
            cv=3,
            n_jobs=-1,
            verbose=1,
            random_state=42
        )
        search.fit(X_train, y_train)
        return search.best_estimator_, search.best_params_

    def train_and_select_model(self) -> ModelTrainerArtifact:
        try:
            logger.info("Loading transformed data")
            X_train = load_object(self.config.X_train_path)
            X_test = load_object(self.config.X_test_path)
            y_train = load_object(self.config.y_train_path)
            y_test = load_object(self.config.y_test_path)

            logger.info("Starting model training with hyperparameter tuning")

            models = {
                "LinearRegression": LinearRegression(),
                "RandomForestRegressor": RandomForestRegressor(random_state=42),
                "GradientBoostingRegressor": GradientBoostingRegressor(random_state=42),
            }

            param_grids = {
                "RandomForestRegressor": {
                    "n_estimators": [50, 100, 200],
                    "max_depth": [None, 10, 20],
                    "min_samples_split": [2, 5, 10],
                },
                "GradientBoostingRegressor": {
                    "n_estimators": [100, 200],
                    "learning_rate": [0.01, 0.1, 0.2],
                    "max_depth": [3, 5, 7],
                }
            }

            best_model_name = None
            best_score = float("-inf")
            best_model = None
            best_metrics = {}

            for name, model in models.items():
                logger.info(f"Training {name}")

                # Hyperparameter tuning if applicable
                if name in param_grids:
                    model, best_params = self._tune_model(model, param_grids[name], X_train, y_train)
                    logger.info(f"Best params for {name}: {best_params}")
                else:
                    model.fit(X_train, y_train)

                # Evaluate model
                metrics = self._evaluate_model(model, X_train, y_train, X_test, y_test)
                logger.info(f"{name} R2 Test Score: {metrics['test_r2']}")

                # Log to MLflow (DagsHub will track this)
                self.track_mlflow(model, metrics, name, X_test)

                # Track the best model
                if metrics["test_r2"] > best_score:
                    best_score = metrics["test_r2"]
                    best_model_name = name
                    best_model = model
                    best_metrics = metrics
            
            save_object(best_model, self.config.model_save_path)

            logger.info(f"Best Model: {best_model_name} (R2: {best_score})")
            logger.info(f"Model saved at: {self.config.model_save_path}")

            return ModelTrainerArtifact(
                model_path=self.config.model_save_path,
                train_score=best_metrics["train_r2"],
                test_score=best_metrics["test_r2"],
                best_model_name=best_model_name
            )

        except Exception as e:
            raise ActivityException(e, sys)