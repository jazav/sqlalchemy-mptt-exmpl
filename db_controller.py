from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.pool import NullPool
from models import DeclarativeBase, Category, CategoryTree
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_mptt import mptt_sessionmaker
from sqlalchemy_mptt import tree_manager
from guid_type import GUID
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

# constants
ON: bool = False
OFF: bool = True


class DatabaseController:

    def __init__(self, settings):
        self.database = settings.DATABASE
        self.clear_db = settings.CLEAR_DB_BEFORE_START
        self.db_schema = settings.DB_SCHEMA
        self.sessions = {}

    def create_engine(self):
        # if it's a first time to launch, we should create a data folder
        self.create_data_folder()
        # TODO: Add Connection Pool here (low priority task)
        engine: Engine = create_engine(URL(**self.database), poolclass=NullPool)

        return engine

    def create_data_folder(self):
        pass
        # Path("../../../data").mkdir(parents=True, exist_ok=True)

    @staticmethod
    def create_tables(engine):
        DeclarativeBase.metadata.create_all(engine, checkfirst=True)

    @staticmethod
    def create_session(engine):
        session: Session = mptt_sessionmaker(sessionmaker(bind=engine))()
        return session

    def clear_tables(self, session):
        if self.clear_db:
            session.query(Category).delete(synchronize_session=False)
            session.query(CategoryTree).delete(synchronize_session=False)

    def open_db(self):
        engine: Engine = self.create_engine()
        self.create_tables(engine)
        session: Session = self.create_session(engine)
        self.sessions[0]: Session = session
        self.clear_tables(session)
        session.commit()

    def close_db(self):
        session: Session = self.sessions.pop(0)
        session.commit()
        session.close()

    def add_category(self, name: str, commit: bool = False) -> Category:
        session: Session = self.sessions[0]
        if session is None:
            raise Exception("session to db is not created")

        category: Category = Category(name=name)
        session.add(category)
        if commit:
            try:
                session.commit()
                # session.flush()
                logger.debug(
                    f'Item {name} is stored in category')

            except SQLAlchemyError as err:
                logger.debug(f'Failed to add {name} to db. Error: {err=}, {type(err)=}')
                session.rollback()
                raise

        return category

    def add_categories(self, *args):
        session: Session = self.sessions[0]
        if session is None:
            raise Exception("session to db is not created")
        if args is None:
            raise Exception("category name isn't passed")
        for arg in args:
            if isinstance(arg, str):
                self.add_category(arg)
            elif isinstance(arg, list):
                for name in arg:
                    self.add_category(name)
            else:
                raise Exception("Unknonw args in add_categories")
        #   session.flush()
        try:
            session.commit()
            logger.debug(
                f'Items {args} are stored in category')
        except SQLAlchemyError as err:
            logger.debug(f'Failed to add {args} to db. Error: {err=}, {type(err)=}')
            session.rollback()
            raise

    def get_category(self, name) -> Category:
        session: Session = self.sessions[0]
        if session is None:
            raise Exception("session is not created")
        category: Category = session.query(Category).filter(Category.name == name).first()
        return category

    def get_max_tree_id(self) -> int:
        """
        Return the maximum of the currently stored tree IDs.
        This is not a thread-safe value, but we use it just for a label.
        """
        session: Session = self.sessions[0]
        if session is None:
            raise Exception("session is not created")
        try:
            max_id: int = session.query(func.max(CategoryTree.tree_id)).one()
            if max_id[0] is None:
                return 0
            return max_id[0]
        except SQLAlchemyError as err:
            logger.exception(err)
        return 0

    def switch_mptt(self, flag: bool, tree_id: int):
        tree_manager.register_events(remove=flag)  # enabled MPTT events back
        if flag:
            logger.debug("MPTT is disabled")
        else:
            session: Session = self.sessions[0]
            if session is None:
                raise Exception("session is not created")
            CategoryTree.rebuild(session, tree_id)  # rebuild lft, rgt value automatically
            logger.debug("MPTT is enabled")

    def add_category_node(self, category: Category, tree_id: int, parent: CategoryTree = None) -> CategoryTree:
        if category is None:
            raise Exception("can't add category, due to it's None ")

        session: Session = self.sessions[0]
        if session is None:
            raise Exception("session is not created")

        if parent is None:
            parent_id = None
        else:
            parent_id = parent.id

        node = CategoryTree(category_id=category.id, parent_id=parent_id, left=0, right=0, tree_id=tree_id)
        session.add(node)
        try:
            session.commit()
            logger.debug(
                f'Item {category.name} is stored in category_tree with id: {node.id}')
        except SQLAlchemyError as err:
            logger.debug(f'Failed to add {category.name} to category_tree. Error: {err=}, {type(err)=}')
            session.rollback()
            raise
        return node
