# Local imports
from .secret import connect

def end(connection, cursor): # 結束和SQL資料庫的會話
    cursor.close()
    connection.commit()
    connection.close()

def link_sql():
    connection = connect()
    cursor = connection.cursor()
    return connection, cursor

# def opWrite(user, user_prop:str, op: str, TABLE = "USER"): # 根據op傳入運算式做+=/-=等以自己原本的值為基準的運算
    # 建立連線
    # connection = connect()
    # cursor = connection.cursor()
    # cursor.execute(f"UPDATE {TABLE} SET {user_prop} = {user_prop}{op} ;")
    # end(connection.cursor)

def write(user_id, user_prop: str, value, cursor, TABLE = "USER"):
    """
    欲變更的使用者、屬性、修改值、欲修改資料表（預設USER,option）
    """
    # 建立連線

    cursor.execute(f'SELECT `uid` {user_prop} FROM `{TABLE}` WHERE `uid`="{user_id}"')
    ret = cursor.fetchall()
    if len(ret) == 0: # 找不到 新增一份
        cursor.execute(f"INSERT INTO `{TABLE}`(uid) VALUE({user_id})")
    cursor.execute(f'UPDATE `{TABLE}` SET {user_prop}="{value}" WHERE `uid`={user_id}')
    # print(f"write {ret} to ({user_prop},{value})")

def read(user_id, user_prop, cursor, TABLE = "USER"):
    # 建立連線

    cursor.execute(f'SELECT {user_prop} FROM `{TABLE}` WHERE `uid`={user_id}')
    ret = cursor.fetchall()
    if len(ret) == 0: # 找不到 新增一份
        cursor.execute(f"INSERT INTO `{TABLE}`(uid) VALUE({user_id})")
        cursor.execute(f'SELECT {user_prop} FROM `{TABLE}` WHERE `uid`={user_id}')
        ret = cursor.fetchall()
    return ret[0][0]

def user_id_exists(user_id, TABLE, cursor):
    cursor.execute(f'SELECT `uid` FROM {TABLE} WHERE `uid`="{user_id}"')
    ret = cursor.fetchall()
    if len(ret) == 0: # 不存在
        return False

    return True

