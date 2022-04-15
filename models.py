import logging
import datetime
from typing import Union
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy import Column, ForeignKey, BigInteger, Identity
import sqlalchemy as sql
import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_mptt.mixins import BaseNestedSets
from guid_type import GUID
from settings import TABLE_ARGS, DB_SCHEMA, TABLE_PREFIX
from settings import PK_TYPE, SEQ_CACHE_SIZE

logger = logging.getLogger(__name__)


class PrefixerMeta(DeclarativeMeta):

    def __init__(cls, name, bases, dict_):
        if '__tablename__' in dict_ and TABLE_PREFIX is not None and TABLE_PREFIX != '':
            cls.__tablename__ = dict_['__tablename__'] = f"{TABLE_PREFIX}_{dict_['__tablename__']}"

        super().__init__(name, bases, dict_)


DeclarativeBase = declarative_base(metaclass=PrefixerMeta)


def is_valid(value: str, *exceptions) -> bool:
    """Check if value is not empty and not in exceptions list"""
    res = value not in (None, '') and len(value.strip()) > 0 and value not in exceptions
    return res

def get_table_key(name: str, prefix: str = TABLE_PREFIX, schema: str = DB_SCHEMA) -> str:
    # Firstly, add prefix to table name
    if is_valid(prefix):
        name = f"{prefix}_{name}"
    # Secondly, add schema to table name with prefix
    if is_valid(schema, "public"):
        name = f"{schema}.{name}"

    return name


def pk_column_maker(column_type: Union[GUID, BigInteger] = PK_TYPE) -> Column:
    if column_type is GUID:
        return Column(column_type, primary_key=True, default=uuid.uuid4)
    else:
        return Column(column_type, Identity(start=1, cycle=False, cache=SEQ_CACHE_SIZE), primary_key=True)


# What is the best type for PK? Read this
# https://www.cybertec-postgresql.com/en/uuid-serial-or-identity-columns-for-postgresql-auto-generated-primary-keys/

class Category(DeclarativeBase):
    __tablename__ = "category"
    __table_args__ = TABLE_ARGS

    id = pk_column_maker()
    name = Column(sql.String(length=256), nullable=False, index=True, unique=True)
    created_at = Column(sql.types.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<Category({})>".format(self.name)


class CategoryTree(DeclarativeBase, BaseNestedSets):
    __tablename__ = "category_tree"
    __table_args__ = TABLE_ARGS

    id = pk_column_maker()
    category_id = Column(PK_TYPE, ForeignKey(get_table_key("category.id")))
    parent_id = Column(PK_TYPE, ForeignKey(get_table_key("category_tree.id")), nullable=True)

    # Attention! To support GUID tree_id we have to use tree_manager.GuidTreesManager from this project
    # tree_id = Column(PK_TYPE, default=uuid.uuid4, nullable=False, index=True)

    created_at = Column(sql.types.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(sql.types.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)

    items = relationship("Category", backref='item')

    @staticmethod
    def update_data(session, category: Category):
        pass

    def __repr__(self):
        return "<Node (%s)>" % self.id
