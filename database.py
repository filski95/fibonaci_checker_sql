import os
from contextlib import contextmanager

from dotenv import load_dotenv
from psycopg2.errors import NumericValueOutOfRange, ProgrammingError
from psycopg2.pool import SimpleConnectionPool

CREATE_FIBON_TABLE = "CREATE TABLE IF NOT EXISTS fibon_results (id SERIAL PRIMARY KEY, fibonaci_nb INTEGER, result BIGINT,searched_times INTEGER);"
CHECK_FIB_DB = "SELECT fibon_results.result FROM fibon_results WHERE fibon_results.fibonaci_nb = %s;"
INSERT_FIB_DB = "INSERT INTO fibon_results (fibonaci_nb,result, searched_times) VALUES (%s,%s,1);"
DELETE_FIB_TABLE = "DROP TABLE IF EXISTS fibon_results;"
UPDATE_FIB_RESULT_COUNTER = """
    UPDATE fibon_results 
    SET searched_times = searched_times + 1 
    WHERE fibon_results.fibonaci_nb = %s;
"""
SHOW_TOP_SEARCHED = """
SELECT * FROM fibon_results 
ORDER BY fibon_results.searched_times DESC 
LIMIT 10;
"""

load_dotenv()
database_uri = os.environ["DATABASE_URI"]
pool = SimpleConnectionPool(minconn=1, maxconn=10, dsn=database_uri)


@contextmanager
def get_connection():
    connection = pool.getconn()
    try:
        yield connection

    finally:
        pool.putconn(connection)


def create_table(connection):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_FIBON_TABLE)


def check_if_fib_already_computed(connection, fib):
    with connection:
        with connection.cursor() as cursor:
            # try except in case no record -> [0] would not work
            cursor.execute(CHECK_FIB_DB, (fib,))
            try:
                # _update_fib_results_counter(cursor, fib)
                fib_from_db = cursor.fetchone()[0]
                cursor.execute(UPDATE_FIB_RESULT_COUNTER, (fib,))  # increase the counter by 1 /// total searched.
                return fib_from_db
            except (TypeError, ProgrammingError):
                return None  # returning None is ok, second part of the app will take care of computing fib. and storing it in db


def insert_fb_into_db(connection, fib, result):
    with connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(INSERT_FIB_DB, (fib, result))
            except NumericValueOutOfRange:
                print("Could not store this nb in the database as it is too big")


def clear_db_table():
    with get_connection() as connection:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(DELETE_FIB_TABLE)
                print("Table has been removed")


def show_top_ones():
    with get_connection() as connection:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(SHOW_TOP_SEARCHED)

                results = cursor.fetchall()
                print("\n")
                for result in results:
                    print(f"Number {result[1]} was searched {result[3]} times")
