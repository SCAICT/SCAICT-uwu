# Future statements
from __future__ import annotations

# Standard imports
import contextlib
import typing

# Third-party imports
import mysql.connector.abstracts
import mysql.connector.errors
import mysql.connector.pooling
import mysql.connector.types

# Local imports
import cog.core.secret


# TODO: replace link_sql()
@contextlib.contextmanager
def mysql_connection() -> typing.Generator[
    tuple[
        mysql.connector.abstracts.MySQLConnectionAbstract,
        mysql.connector.abstracts.MySQLCursorAbstract,
    ],
    typing.Any,
    None,
]:
    """
    Returns:
        typing.Generator[tuple[mysql.connector.abstracts.MySQLConnectionAbstract, mysql.connector.abstracts.MySQLCursorAbstract], typing.Any, None]:

    Raises:
        RuntimeError:
        TypeError:
        mysql.connector.errors.Error:
    """

    connection: mysql.connector.abstracts.MySQLConnectionAbstract | None = None
    cursor: mysql.connector.abstracts.MySQLCursorAbstract | None = None

    try:
        connection = typing.cast(
            mysql.connector.abstracts.MySQLConnectionAbstract, cog.core.secret.connect()
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


def end(
    connection: (
        mysql.connector.pooling.PooledMySQLConnection
        | mysql.connector.abstracts.MySQLConnectionAbstract
    ),
    cursor: mysql.connector.abstracts.MySQLCursorAbstract | typing.Any,
) -> None:
    """
    結束和SQL資料庫的會話

    Parameters:
        connection (mysql.connector.pooling.PooledMySQLConnection | mysql.connector.abstracts.MySQLConnectionAbstract):
        cursor (mysql.connector.abstracts.MySQLCursorAbstract | typing.Any):
    """

    cursor.close()
    connection.commit()
    connection.close()


def link_sql() -> tuple[
    mysql.connector.pooling.PooledMySQLConnection
    | mysql.connector.abstracts.MySQLConnectionAbstract,
    mysql.connector.abstracts.MySQLCursorAbstract | typing.Any,
]:
    """
    Returns:
        tuple[mysql.connector.pooling.PooledMySQLConnection | mysql.connector.abstracts.MySQLConnectionAbstract, mysql.connector.abstracts.MySQLCursorAbstract | typing.Any]:
    """

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
) -> dict[str, mysql.connector.types.RowItemType] | None:
    """
    Parameters:
        table (str):
        key_name (str):
        value (mysql.connector.types.MySQLConvertibleType):

    Returns:
        dict[str, mysql.connector.types.RowItemType] | None:
    """

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


def write(
    user_id,
    user_prop: str,
    value,
    cursor: mysql.connector.abstracts.MySQLCursorAbstract | typing.Any,
    table: str = "user",
) -> None:
    """
    欲變更的使用者、屬性、修改值、欲修改資料表（預設user, option）

    XXX: this implement have the risk about SQL injection

    Parameters:
        user_id:
        user_prop (str):
        value:
        cursor (mysql.connector.abstracts.MySQLCursorAbstract | typing.Any):
        table (str):
    """

    # 建立連線

    cursor.execute(f'SELECT `uid` FROM `{table}` WHERE `uid`="{user_id}"')
    ret = cursor.fetchall()

    if len(ret) == 0:  # 找不到 新增一份
        cursor.execute(f"INSERT INTO `{table}`(uid) VALUE({user_id})")

    cursor.execute(f'UPDATE `{table}` SET {user_prop}="{value}" WHERE `uid`={user_id}')

    # print(f"write {ret} to ({user_prop},{value})")


def read(
    user_id,
    user_prop,
    cursor: mysql.connector.abstracts.MySQLCursorAbstract | typing.Any,
    table: str = "user",
) -> mysql.connector.types.RowItemType | typing.Any:
    """
    Parameters:
        user_id:
        user_prop:
        cursor (mysql.connector.abstracts.MySQLCursorAbstract | typing.Any):
        table (str):

    Returns:
        mysql.connector.types.RowItemType | typing.Any:
    """

    # 建立連線

    cursor.execute(f"SELECT {user_prop} FROM `{table}` WHERE `uid`={user_id}")
    ret = cursor.fetchall()

    if len(ret) == 0:  # 找不到 新增一份
        cursor.execute(f"INSERT INTO `{table}`(uid) VALUE({user_id})")
        cursor.execute(f"SELECT {user_prop} FROM `{table}` WHERE `uid`={user_id}")
        ret = cursor.fetchall()

    return ret[0][0]


def user_id_exists(
    user_id,
    table: str,
    cursor: mysql.connector.abstracts.MySQLCursorAbstract | typing.Any,
) -> bool:
    """
    Parameters:
        user_id:
        table (str):
        cursor (mysql.connector.abstracts.MySQLCursorAbstract | typing.Any):

    Returns:
        bool:
    """

    cursor.execute(f'SELECT `uid` FROM {table} WHERE `uid`="{user_id}"')
    ret = cursor.fetchall()

    if len(ret) == 0:  # 不存在
        return False

    return True
