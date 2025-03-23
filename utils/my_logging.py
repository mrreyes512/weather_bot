import argparse
import asyncio
import logging
import os
import random
import sys

import pandas as pd
import pendulum
import urllib3
from dotenv import load_dotenv

# from utils.my_llm import MY_LLM
# from utils.my_weather import MY_Weather
# from utils.notify import MY_CiscoWebex

class MY_Logger:
    def __init__(self, log_file: str, log_level=logging.INFO):
        self.log_file = log_file
        self.log_level = log_level
        self.log = logging.getLogger()
        self._configure_logger()

    def _configure_logger(self):
        self.log.setLevel(self.log_level)

        # Add handlers to the logger
        self.log.addHandler(self._get_stdout_handler())
        self.log.addHandler(self._get_file_handler())

    def _get_formatter(self):
        """Create and return a logging formatter."""
        return logging.Formatter(
            '%(asctime)s | %(levelname).4s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def _get_stdout_handler(self):
        """Create and return a stream handler for console output."""
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(self._get_formatter())
        return stdout_handler

    def _get_file_handler(self):
        """Create and return a file handler for logging to a file."""
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self._get_formatter())
        return file_handler

    def get_logger(self):
        return self.log


# Usage
if __name__ == "__main__":
    # Get current date
    now = pendulum.now().format('YYYY-MM-DD')

    # Set up logging
    directory_name = os.path.basename(os.getcwd())
    log_file = os.path.join(os.getcwd(), f"{directory_name}.log")
    log = Logger(log_file=log_file, log_level=logging.DEBUG).get_logger()

    log.info(f"Test info: {now}")
    log.warning('Testing logging to file')
    log.error('Testing error logging')
    log.debug('Testing debug logging')
