import mysql.connector

#初始化資料庫程式，從創建表格開始
connection = mysql.connector.connect(host="172.233.85.95",
                                    port="3306",
                                    user="iach",  
                                    passwd="Mew_mewCat@>",
                                    database="DCSQLtest"
)
cursor=connection.cursor()

cursor.execute("USE DCSQLtest")
cursor.execute("CREATE TABLE `USER`(uid BIGINT NOT NULL,\
                                    point INT NOT NULL DEFAULT 0,\
                                    ticket INT NOT NULL DEFAULT 0,\
                                    charge_combo INT NOT NULL DEFAULT 0,\
                                    next_lottery INT NOT NULL DEFAULT 0,\
                                    last_charge DATETIME NOT NULL DEFAULT '1970-01-01 00::00:00',\
                                    last_comment DATE NOT NULL DEFAULT '1970-01-01',\
                                    today_comments INT NOT NULL DEFAULT 0,\
                                    PRIMARY KEY (`uid`)\
                                    )"
              )
cursor.execute("CREATE TABLE `CommentPoints`(seq INT AUTO_INCREMENT PRIMARY KEY,\
                                              user_id BIGINT NOT NULL,\
                                              times INT NOT NULL DEFAULT 2,\
                                              next_reward INT NOT NULL DEFAULT 1,\
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