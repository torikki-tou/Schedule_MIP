import mysql.connector
from mysql.connector import errorcode
import config


def connection(function):
    def wrapper(*args, **kwargs):
        con, cursor, response = None, None, None

        try:
            con = mysql.connector.connect(**config.DB_PARAMS)
            con.autocommit = True

            if con.is_connected():
                cursor = con.cursor(dictionary=True)
                response = function(cursor, *args, **kwargs)
                print('Функция {} успешно применена'.format(function))

        except mysql.connector.Error as e:
            print('Ошибка подключения к базе данных:', e)

        finally:
            if con is not None and con.is_connected():
                cursor.close()
                con.close()

        return response
    return wrapper


@connection
def new_user(cursor, pk, username):
    try:
        cursor.execute("INSERT INTO users (id, username, status) VALUES ({}, '{}', {})".format(
            pk, username,
            config.Status.S_START.value))
    except mysql.connector.Error as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            pass
        else:
            print(e)


@connection
def get_status(cursor, pk):
    cursor.execute("SELECT status FROM users WHERE id={}".format(pk))
    result = cursor.fetchone()
    if result:
        return int(result['status'])


@connection
def set_status(cursor, pk, status):
    cursor.execute("UPDATE users SET status={} WHERE id={}".format(status, pk))


@connection
def get_group(cursor, pk: int):
    cursor.execute("SELECT uni_group FROM users WHERE id={}".format(pk))
    result = cursor.fetchone()
    if result:
        response = result['uni_group']
        return response


@connection
def set_group(cursor, pk: int, group: str):
    cursor.execute("UPDATE users SET uni_group='{}' WHERE id={}".format(group, pk))


@connection
def get_group_key(cursor, group: str) -> str:
    cursor.execute("SELECT api_key FROM uni_groups WHERE id='{}'".format(group))
    return cursor.fetchone()['api_key']


@connection
def group_exists(cursor, group: str) -> bool:
    cursor.execute("SELECT id FROM uni_groups WHERE id='{}'".format(group))
    return cursor.fetchone() is not None


@connection
def get_all_groups(cursor) -> list:
    cursor.execute("SELECT id FROM uni_groups")
    return list(row['id'] for row in cursor.fetchall())
