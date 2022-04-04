# settings.py
import os
from pathlib import Path
from distutils.util import strtobool
import logging
from dotenv import load_dotenv
import sys

logger = logging.getLogger(__name__)
PROJECT_DIR: str = os.path.dirname(os.path.abspath(__file__))
# Connect the path with your '.env' file name
load_dotenv(os.path.join(PROJECT_DIR, '.env'))


def get_db_password(key, default):
    value = os.getenv(key, default)
    if os.path.isfile(value):
        return Path(value).read_text().rstrip("\n")
    return value

LOG_FORMAT: str = os.getenv("LOG_FORMAT")
LOG_DATE: str = os.getenv("LOG_DATE")
LOG_LEVEL: str = os.getenv("LOG_LEVEL")
if LOG_LEVEL is None:
    LOG_LEVEL: int = logging.INFO

logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE, level=LOG_LEVEL)

# clear table admission before append new data
CLEAR_DB_BEFORE_START = bool(strtobool(os.getenv("CLEAR_DB_BEFORE_START", 'False')))
TABLE_ARGS = None

db_file = os.getenv("SQLITE_FILE")

if db_file:

    DATABASE: dict[str, str] = {
        'drivername': 'sqlite',
        'database': db_file
    }
    DB_SCHEMA = ''
else:
    DB_SCHEMA = os.getenv("POSTGRES_SCHEMA", '')
    if DB_SCHEMA == "":
        TABLE_ARGS = None
    else:
        TABLE_ARGS = {'schema': DB_SCHEMA}

    user: str = os.getenv("POSTGRES_USER")
    if not user:
        raise Exception("Database user is empty")

    password: str = os.getenv("DBUSER_PASSWORD")
    if password:
        password_file = os.getenv("DBUSER_PASSWORD_FILE")
        if password_file:
            logger.warning(
                f"*** DBUSER_PASSWORD_FILE is ignored, DBUSER_PASSWORD is used to define database password ***")
    else:
        password: str = get_db_password(key="DBUSER_PASSWORD_FILE", default='')

    if not password:
        raise Exception("Database password is empty")

    port: str = os.getenv("POSTGRES_PORT")
    if not port:
        raise Exception("Database port is empty")

    db: str = os.getenv("POSTGRES_DB")
    if not db:
        raise Exception("Database db alias is empty")

    host: str = os.getenv("POSTGRES_HOST")
    if not host:
        raise Exception("Database db host is empty")

    logger.info(f"*** buypremium uses Postgresql database {db} ***")
    DATABASE: dict[str, str] = {
        'drivername': 'postgresql',
        'host': host,
        'port': port,
        'username': user,
        'password': password,
        'database': db
    }
