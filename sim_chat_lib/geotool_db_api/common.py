import logging
import os
import asyncpg


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


async def create_pool_a(*args, **kwargs):
    global CONXN_POOL
    if not CONXN_POOL:
        CONXN_POOL = await asyncpg.create_pool(**get_db_from_env())
        # CONXN_POOL = ThreadedConnectionPool(1, 10, *args, **kwargs)


async def execute_sql_update_a(query, *args):
    # loop = asyncio.get_event_loop()
    # print("Executing update sql")
    # print(*args)
    return await execute_sql_a(query, *args)


async def execute_sql_fetchval_a(query, *args):
    # print(*args)
    global CONXN_POOL
    if not CONXN_POOL:
        await create_pool_a(**get_db_from_env())

    async with CONXN_POOL.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchval(query, *args)
            return result


async def execute_sql_a(query, *args):
    # print(*args)
    global CONXN_POOL
    if not CONXN_POOL:
        await create_pool_a(**get_db_from_env())

    async with CONXN_POOL.acquire() as connection:
        async with connection.transaction():
            await connection.execute(query, *args)


def execute_sql_get_a(query, *args):
    # loop = asyncio.get_event_loop()

    rows = execute_sql_fetchval_a(query, *args)

    return rows
