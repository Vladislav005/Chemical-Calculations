from config import * 
import pymysql
import sqlite3


def create_mysql_connection():
    try:
        connection = pymysql.connect(
            host=host,
            port=3306,
            user=user_name,
            password=password,
            database=db_name,  # db_chem
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Connected ")
        print('#' * 80)

    except Exception as ex:
        print("Connection error.....................")
        print(ex)
    return connection

def create_sqlite_connection():
    try:
        connection = sqlite3.connect(sqlite_file_name)
        connection.row_factory = sqlite3.Row
        print("Connected ")
        print('#' * 80)
    except Exception as ex:
        print('Connection error......................')
        print(ex)
    return connection

def create_connection():
    if connection_type == 'global':
        return create_mysql_connection()
    elif connection_type == 'local':
        return create_sqlite_connection()