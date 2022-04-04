
from typing import Optional, Any
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
import uuid
import hashlib


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    https://docs.sqlalchemy.org/en/14/core/custom_types.html#backend-agnostic-guid-type
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value

    @staticmethod
    def build(value: Any) -> Optional[UUID]:
        if value is None or isinstance(value, uuid.UUID):
            return value
        else:
            if isinstance(value, str):
                value_str: str = value
            else:
                try:
                    value_str: str = str(value)
                except TypeError:
                    err_msg: str = f"Can't build GUID du to incorrect type of value."
                    raise Exception(err_msg)

            value = uuid.UUID(hashlib.md5(value_str.encode('utf-8')).hexdigest())

        return value
