import logging
import datetime
from sqlalchemy import Column, Boolean, ForeignKey, UniqueConstraint
import sqlalchemy as sql
from guid_type import GUID
import uuid
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_mptt.mixins import BaseNestedSets
from settings import TABLE_ARGS, DB_SCHEMA

logger = logging.getLogger(__name__)

DeclarativeBase = declarative_base()


def add_schema_name(table_name):
    if DB_SCHEMA == '':
        return table_name
    else:
        return DB_SCHEMA + '.' + table_name


class Category(DeclarativeBase):
    __tablename__ = "category"
    __table_args__ = TABLE_ARGS

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(sql.String(length=256), nullable=False, index=True, unique=True)
    created_at = Column(sql.types.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<Category({})>".format(self.url)


class CategoryTree(DeclarativeBase, BaseNestedSets):
    __tablename__ = "category_tree"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    category_id = Column(GUID, ForeignKey(add_schema_name("category.id")))
    items = relationship("Category", backref='item')
    created_at = Column(sql.types.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(sql.types.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)

    @staticmethod
    def update_data(session, category: Category):
        pass

    def __repr__(self):
        return "<Node (%s)>" % self.id
