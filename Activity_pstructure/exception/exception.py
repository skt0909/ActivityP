import sys
from Activity_pstructure.logging.logger import logger

# exception.py

class ActivityException(Exception):
    def __init__(self, error: Exception, sys_module):
        super().__init__(str(error))
        self.error = error
        self.traceback_info = sys_module.exc_info()
        logger.error(f"ActivityException raised: {self}", exc_info=self.traceback_info)

    def __str__(self):
        exc_type, exc_obj, exc_tb = self.traceback_info
        return (
            f"{str(self.error)} | "
            f"File: {exc_tb.tb_frame.f_code.co_filename}, "
            f"Line: {exc_tb.tb_lineno}, "
            f"Type: {exc_type.__name__}"
        )
