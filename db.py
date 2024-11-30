from config import host, user_name, password, db_name
import pymysql


def create_connection():
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