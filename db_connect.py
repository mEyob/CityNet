"""
--db_connect.py--
PostgreSQL/TimeScaleDB interface for Kafka Consumers
"""

import psycopg2
from psycopg2.extras import execute_values
import os
import time
import json

CONNECTION = json.loads(os.environ["CONNECTION"])


def insert_in_db(table_name, records, num_of_records, page_size=100):
    '''
    A function for writing rows into database.
    :param table_statement: the `INSERT INTO` statement to be executed
    :values: new values to be inserted in the database
    '''
    con = None
    sql_statement = {
        "sensors":
        "INSERT INTO aot.sensors (path, uom, min, max, data_sheet) VALUES %s;",
        "observations":
        "INSERT INTO aot.observations (sensor_path, ts, value, node_vsn) VALUES %s;",
        "nodes": "INSERT INTO aot.nodes(vsn, long, lat) VALUES %s;"
    }
    try:
        con = psycopg2.connect(**CONNECTION)
    except Exception as ex:
        print(
            "Exception encountered while trying to connect to database with: ")
        print("{}".format(CONNECTION))
        print(str(ex))
    if con:
        try:
            cursor = con.cursor()
            start = time.perf_counter()
            execute_values(cursor,
                           sql_statement[table_name],
                           records,
                           page_size=page_size)
            con.commit()
            end = time.perf_counter()
            print("{}: Inserted {} rows in {} seconds".format(
                int(time.time()), num_of_records, end - start))
        except psycopg2.DatabaseError as ex:
            con.rollback()
            print("Exception encountered: Psycopg2")
            print(str(ex))
        finally:
            con.close()
