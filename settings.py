# settings.py
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

PROJECT_DIR: str = os.path.dirname(os.path.abspath(__file__))
# Connect the path with your '.env' file name
load_dotenv(os.path.join(PROJECT_DIR, '.env'))

LOG_FORMAT: str = os.getenv("LOG_FORMAT")
LOG_DATE: str = os.getenv("LOG_DATE")
LOG_LEVEL: str = os.getenv("LOG_LEVEL")
if LOG_LEVEL is None:
    LOG_LEVEL: int = logging.INFO

logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE, level=LOG_LEVEL)

# import database settings to provide for all modules
from db_settings import *