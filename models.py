import logging
import datetime

from sqlalchemy import Column, ForeignKey, BigInteger, Identity, Integer
import sqlalchemy as sql
import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_mptt.mixins import BaseNestedSets
from settings import TABLE_ARGS, DB_SCHEMA
from sqlalchemy.schema import _get_table_key
from settings import PK_TYPE, SEQ_CACHE_SIZE

logger = logging.getLogger(__name__)

DeclarativeBase = declarative_base()


# What is the best type for PK? Read this
# https://www.cybertec-postgresql.com/en/uuid-serial-or-identity-columns-for-postgresql-auto-generated-primary-keys/

class Category(DeclarativeBase):
    __tablename__ = "category"
    __table_args__ = TABLE_ARGS

    # id = Column(PK_TYPE, primary_key=True, default=uuid.uuid4)
    id = Column(PK_TYPE, Identity(start=1, cycle=False, cache=SEQ_CACHE_SIZE),
                primary_key=True)
    name = Column(sql.String(length=256), nullable=False, index=True, unique=True)
    created_at = Column(sql.types.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<Category({})>".format(self.name)


class CategoryTree(DeclarativeBase, BaseNestedSets):
    __tablename__ = "category_tree"
    __table_args__ = TABLE_ARGS

    # id = Column(PK_TYPE, primary_key=True, default=uuid.uuid4)
    id = Column(PK_TYPE, Identity(start=1, cycle=False, cache=SEQ_CACHE_SIZE),
                primary_key=True)

    # category_id = Column(PK_TYPE, ForeignKey(_get_table_key("category.id", DB_SCHEMA)))
    category_id = Column(PK_TYPE, ForeignKey(_get_table_key("category.id", DB_SCHEMA)))
    parent_id = Column(PK_TYPE, ForeignKey(_get_table_key("category_tree.id", DB_SCHEMA)), nullable=True)

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
