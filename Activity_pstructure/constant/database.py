from pathlib import Path

DATABASE_NAME = "SKT"
COLLECTION_NAME = "ActivityData"

PREPROCESSED_DATA_PATH = str(Path(__file__).parent.parent / "notebook" / "preprocessed_data.csv")

X_TRAIN_PATH = r"artifacts/transformed/X_train.pkl"
X_TEST_PATH = r"artifacts/transformed/X_test.pkl"
Y_TRAIN_PATH = r"artifacts/transformed/y_train.pkl"
Y_TEST_PATH = r"artifacts/transformed/y_test.pkl"
TRANSFORMER_PATH = r"artifacts/transformed/transformer.pkl"

BEST_MODEL_PATH = r"artifacts/model/model.pkl"

