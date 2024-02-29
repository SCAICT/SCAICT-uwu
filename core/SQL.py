import mysql.connector
connection = mysql.connector.connect(host="",
                                      port="",
                                      user="",  
                                      passwd="",
                                      database=""
)


def write(userId, property, value):#欲更改的使用者,屬性,修改值
    cursor.execute(f'SELECT `uid`,{property} FROM `USER` WHERE `uid`="{userId}"')
    RET=cursor.fetchall()
    if (len(RET) !=0):#有 select 到東西，長度不為0
        cursor.execute(f'UPDATE `USER` SET {str(property)}={value} WHERE `uid`={userId}')
        print(RET)
    else:
        print("找不到")#創造一份?
        # cursor.execute("INSERT INTO `USER` VALUE(898141506588770334,999,0,1,2,3,'2024-2-29','2024-2-28')")
    pass
def read(userId, property):
    cursor.execute(f'SELECT {property} FROM `USER` WHERE `uid`="{userId}"')
    RET=cursor.fetchall()
    return RET[0][0]
if __name__=="__main__":
    cursor=connection.cursor()
    # write(898141506588770334, "point", 1000)
    read(89811506588770334,"point")
    print("done")
    cursor.close()
    connection.commit()
    connection.close()