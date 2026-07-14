# Future statements
from __future__ import annotations

# Standard imports
import contextlib
import typing

# Third-party imports
import mysql.connector.connection_cext
import mysql.connector.cursor_cext
import mysql.connector.types
import mysql.connector.errors

# Local imports
import cog.core.secret


# TODO: replace link_sql()
@contextlib.contextmanager
def mysql_connection():
    connection: mysql.connector.connection_cext.CMySQLConnection | None = None
    cursor: mysql.connector.cursor_cext.CMySQLCursor | None = None

    try:
        connection = typing.cast(
            mysql.connector.connection_cext.CMySQLConnection, cog.core.secret.connect()
        )
        if connection is None:
            raise RuntimeError("Cannot connect to database")
        cursor = connection.cursor()
        yield (connection, cursor)
        connection.commit()
    except TypeError:
        print("Please setup .env correctly.")
        raise
    except mysql.connector.errors.Error:
        if connection:
            connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def end(connection, cursor):  # 結束和SQL資料庫的會話
    cursor.close()
    connection.commit()
    connection.close()


def link_sql():
    connection = cog.core.secret.connect()
    cursor = connection.cursor()
    return connection, cursor


# def opWrite(user, user_prop:str, op: str, table = "user"): # 根據op傳入運算式做+=/-=等以自己原本的值為基準的運算
# 建立連線
# connection = connect()
# cursor = connection.cursor()
# cursor.execute(f"UPDATE {table} SET {user_prop} = {user_prop}{op} ;")
# end(connection.cursor)


def fetchone_by_primary_key(
    table: str, key_name: str, value: mysql.connector.types.MySQLConvertibleType
):
    with mysql_connection() as c:
        _, cursor = c
        query = f"SELECT * FROM `{table}` WHERE `{key_name}` = %s"
        cursor.execute(query, (value,))
        result = cursor.fetchall()

        if len(result) == 0:
            return None

        if len(result) != 1:
            raise ValueError("Result have multiple rows.")

        row = result[0]
        field_names = cursor.column_names

        return dict(zip(field_names, row))


# XXX: this implement have the risk about SQL injection
def write(user_id, user_prop: str, value, cursor, table: str = "user") -> None:
    """
    欲變更的使用者、屬性、修改值、欲修改資料表（預設user, option）
    """
    # 建立連線

    cursor.execute(f'SELECT `uid` FROM `{table}` WHERE `uid`="{user_id}"')
    ret = cursor.fetchall()
    if len(ret) == 0:  # 找不到 新增一份
        cursor.execute(f"INSERT INTO `{table}`(uid) VALUE({user_id})")
    cursor.execute(f'UPDATE `{table}` SET {user_prop}="{value}" WHERE `uid`={user_id}')
    # print(f"write {ret} to ({user_prop},{value})")


def read(user_id, user_prop, cursor, table="user"):
    # 建立連線

    cursor.execute(f"SELECT {user_prop} FROM `{table}` WHERE `uid`={user_id}")
    ret = cursor.fetchall()
    if len(ret) == 0:  # 找不到 新增一份
        cursor.execute(f"INSERT INTO `{table}`(uid) VALUE({user_id})")
        cursor.execute(f"SELECT {user_prop} FROM `{table}` WHERE `uid`={user_id}")
        ret = cursor.fetchall()
    return ret[0][0]


def user_id_exists(user_id, table, cursor):
    cursor.execute(f'SELECT `uid` FROM {table} WHERE `uid`="{user_id}"')
    ret = cursor.fetchall()
    if len(ret) == 0:  # 不存在
        return False

    return True
