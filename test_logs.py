import sys
from Activity_pstructure.exception.exception import ActivityException
from Activity_pstructure.logging.logger import logger

try:
    raise ValueError("Some inner error")
except Exception as e:  
    logger.error("An exception occurred", exc_info=True)
    raise ActivityException(e, sys)