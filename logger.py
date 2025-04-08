from logging import getLogger, StreamHandler, Formatter, FileHandler, INFO, WARNING, ERROR
from math import log
import os
import sys
from typing import List, Dict, Any, Tuple, Optional, Union
from utils import makedirs


class CustomLogger:
    def __init__(self, log_dir: Optional[str] =None, log_file: Optional[str] =None, log_name: Optional[str]=None):
        self.log_dir = log_dir if log_dir else './logs'
        self.log_file = log_file if log_file else 'default.log'
        self.log_name = log_name if log_name else 'CustomLogger'
        self.__initialize_logger(self.log_dir)
        
        self.logger = getLogger(self.log_name)
        self.logger.setLevel(INFO)
        self.formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # self.stream_handler = StreamHandler(sys.stdout)
        # self.stream_handler.setFormatter(self.formatter)
        # self.logger.addHandler(self.stream_handler)

        self.file_handler = FileHandler(os.path.join(self.log_dir, self.log_file))
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
    
    @classmethod
    def __initialize_logger(cls, log_dir:str):
        if not os.path.exists(log_dir):
            makedirs(log_dir)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def exception(self, msg: str):
        self.logger.exception(msg)

    def debug(self, msg: str):
        self.logger.debug(msg)