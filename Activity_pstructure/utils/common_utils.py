import os
import pandas as pd
import pickle
from Activity_pstructure.logging import logger

def save_dataframe(df: pd.DataFrame, output_dir: str, output_filename: str, logger=None):
    try:
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, output_filename)
        df.to_csv(file_path, index=False)
        if logger:
            logger.info(f"DataFrame saved to {file_path}")
        else:
            print(f"DataFrame saved to {file_path}")
        return file_path
    except Exception as e:
        raise Exception(f"Failed to save DataFrame: {e}")

def save_object(obj, file_path: str):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as file_obj:
        pickle.dump(obj, file_obj)