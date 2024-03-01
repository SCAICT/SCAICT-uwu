import mysql.connector
#初始化資料庫程式，從創建表格開始
connection = mysql.connector.connect(host="",
                                      port="",
                                      user="",  
                                      passwd=""
)
cursor=connection.cursor()

cursor.execute("USE DCSQLtest ")
cursor.execute("CREATE TABLE `USER`(uid BIGINT NOT NULL,\
                                    point INT,\
                                    ticket INT,\
                                    charge_combo INT,\
                                    next_lottery INT ,\
                                    num_comment INT,\
                                    last_charge DATETIME,\
                                    last_comment DATETIME,\
                                    PRIMARY KEY (`uid`)\
                                    )"
              )
cursor.execute("CREATE TABLE `CommentPoints`(seq INT AUTO_INCREMENT PRIMARY KEY,\
                                              user_id BIGINT NOT NULL,\
                                              times INT,\
                                              next_reward INT,\
                                              FOREIGN KEY (`user_id`) REFERENCES USER(`uid`) ON DELETE CASCADE\
                                          )"
  )


#查看所有databases
# cursor.execute("SHOW DATABASES")
# RET=cursor.fetchall()
# print(RET)
print("done")
cursor.close()
connection.commit()
connection.close()