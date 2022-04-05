# main.py
import logging
import os
import time
from python_settings import settings #don't delete it!
import settings as app_settings
from db_controller import DatabaseController, ON, OFF
import uuid

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    start_time = time.monotonic()

    dbc = DatabaseController(app_settings)
    dbc.open_db()
    logger.info(f"data base is opened")
    try:
        names: list = []
        count: int = int(os.getenv("CATEGORY_COUNT", 5))

        for i in range(count):
            salt: str = uuid.uuid4().hex
            names.append(f"category_{i+1}_{salt}")

        logger.debug(f"names: {names[0]}..{names[count - 1]}")

        dbc.add_categories(names)

        salt: str = uuid.uuid4().hex
        cat = dbc.add_category(name=f"root_{salt}", commit=True)

        # You should pay your attention that this code is not thread-safe.
        # It's not a problem, because it's not a real-life application.
        # But if you want to use this code in a real-life application,
        # you should use a database with a lock.

        # dbc.lock_db() or something like that
        # try:
        tree_id = dbc.get_max_tree_id()
        tree_id = tree_id + 1

        root = dbc.add_category_node(category=cat, tree_id=tree_id)
        # finally:
        #   dbc.unlock()

        # MPTT will refresh every node for any CRUD operation
        # In order to speed up set of CRUD operations we can switch refreshing process off and switch it on later
        dbc.switch_mptt(flag=OFF, tree_id=tree_id)
        try:
            # apply a bunch of CRUD
            for i in range(count):
                cat = dbc.get_category(name=names[i])
                node = dbc.add_category_node(tree_id=tree_id, category=cat, parent=root)
        finally:
            # switch MPTT refresh on
            dbc.switch_mptt(flag=ON, tree_id=tree_id)

        logger.info(f"all data has been written successfully")
    finally:
        dbc.close_db()
        logger.info(f"data base is closed")

    logger.info(f"elapsed time: {time.monotonic() - start_time}")
