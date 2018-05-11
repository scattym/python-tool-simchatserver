import psycopg2
import logging
import os
import asyncpg
import asyncio
from psycopg2.pool import ThreadedConnectionPool

logger = logging.getLogger(__name__)

CONXN_POOL = None


def get_db_from_env():
    data = {
        "database": os.environ.get('DBNAME', 'geotool'),
        'user': os.environ.get('DBUSER', 'django'),
        'host': os.environ.get('DBHOST', '127.0.0.1'),
        'password': os.environ.get('DBPASS', 'tiapw4gd2u'),
        'port': os.environ.get('DBPORT', 5432),
        # 'timeout': os.environ.get("DBTIMEOUT", None)

    }
    return data


async def create_pool(*args, **kwargs):
    global CONXN_POOL
    if not CONXN_POOL:
        CONXN_POOL = await asyncpg.create_pool(**get_db_from_env())
        # CONXN_POOL = ThreadedConnectionPool(1, 10, *args, **kwargs)


def execute_sql_update(query, *args):
    loop = asyncio.get_event_loop()
    global CONXN_POOL
    if not CONXN_POOL:
        loop.run_until_complete(create_pool(**get_db_from_env()))
    rows = loop.run_until_complete(execute_sql(query, *args))

    return rows


async def execute_sql(query, *args):
    async with CONXN_POOL.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchval(query, *args)
            return result


def execute_sql_get(query, *args):
    loop = asyncio.get_event_loop()
    global CONXN_POOL
    if not CONXN_POOL:
        loop.run_until_complete(create_pool(**get_db_from_env()))
    rows = loop.run_until_complete(execute_sql(query, *args))

    return rows
