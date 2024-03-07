from .secret import connect

def end(connection,cursor):#結束和SQL資料庫的會話
    cursor.close()
    connection.commit()
    connection.close()
def linkSQL():
    connection=connect()
    cursor=connection.cursor()
    return connection,cursor
# def opWrite(user,property:str,op:str,TABLE="USER"):#根據op 傳入運算式做+=/-=等以自己原本的值為基準的運算
#     #建立連線
#     connection=connect()
#     cursor=connection.cursor()
#     cursor.execute(f"UPDATE {TABLE} SET {property} = {property}{op} ;")
#     end(connection.cursor)
def write(userId, property:str, value,cursor,TABLE="USER"):#欲更改的使用者,屬性,修改值,欲修改表格(預設USER,option)
    #建立連線
    
    cursor.execute(f'SELECT `uid` {property} FROM `{TABLE}` WHERE `uid`="{userId}"')
    RET=cursor.fetchall()
    if len(RET) ==0:#找不到 創造一份
        cursor.execute(f"INSERT INTO `{TABLE}`(uid) VALUE({userId})")
    cursor.execute(f'UPDATE `{TABLE}` SET {property}="{value}" WHERE `uid`={userId}')
    # print(f"write {RET} to ({property},{value})")
def read(userId, property,cursor,TABLE="USER"):
    #建立連線
    
    cursor.execute(f'SELECT {property} FROM `{TABLE}` WHERE `uid`={userId}')
    RET=cursor.fetchall()
    if len(RET) ==0:#找不到 創造一份
        cursor.execute(f"INSERT INTO `{TABLE}`(uid) VALUE({userId})")
        cursor.execute(f'SELECT {property} FROM `{TABLE}` WHERE `uid`={userId}')
        RET=cursor.fetchall()
    return RET[0][0]


def isExist(userId,table,cursor):
    cursor.execute(f'SELECT `uid` FROM {table} WHERE `uid`="{userId}"')
    RET=cursor.fetchall()
    if (len(RET)==0):#不存在
        return False
    else:
        return True
    

# if __name__=="__main__":
#     # write(898141506588770334, "point", 1000)
#     print(read(89811506588770334,"point"))
#     print("done")
 