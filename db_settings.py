# db_settings.py
import os
from distutils.util import strtobool
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _get_db_password(key, default):
    value = os.getenv(key, default)
    if os.path.isfile(value):
        return Path(value).read_text().rstrip("\n")
    return value


# clear tables before append new data
CLEAR_DB_BEFORE_START = bool(strtobool(os.getenv("CLEAR_DB_BEFORE_START", 'False')))
TABLE_ARGS = None

db_file = os.getenv("SQLITE_FILE")

dialect = None
PK_TYPE = None
SEQ_CACHE_SIZE: int = 200

if db_file:
    from sqlalchemy.dialects import sqlite

    dialect = sqlite.dialect()
    PK_TYPE = sqlite.INTEGER

    DATABASE: dict[str, str] = {
        'drivername': 'sqlite',
        'database': db_file
    }
    DB_SCHEMA = None
else:
    from sqlalchemy.dialects import postgresql

    dialect = postgresql.dialect()
    PK_TYPE = postgresql.BIGINT

    DB_SCHEMA = os.getenv("POSTGRES_SCHEMA", None)
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
        password: str = _get_db_password(key="DBUSER_PASSWORD_FILE", default='')

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

    logger.info(f"*** Postgresql database {db} ***")
    DATABASE: dict[str, str] = {
        'drivername': 'postgresql',
        'host': host,
        'port': port,
        'username': user,
        'password': password,
        'database': db
    }

logger.debug(f"Using dialect: {dialect.name}")