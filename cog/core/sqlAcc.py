import mysql.connector
from .SQL import linkSQL

connection,cursor=linkSQL()

cursor.execute("USE DCSQLtest")#use your database
cursor.execute("CREATE TABLE `USER`(uid BIGINT NOT NULL,\
                                    loveuwu TINYINT(1) NOT NULL DEFAULT 0 \
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
                                              uid BIGINT NOT NULL,\
                                              times INT NOT NULL DEFAULT 2,\
                                              next_reward INT NOT NULL DEFAULT 1,\
                                              FOREIGN KEY (`uid`) REFERENCES USER(`uid`) ON DELETE CASCADE\
                                          )"
  )
cursor.execute("\
               CREATE TABLE `game` (seq BIGINT NOT NULL DEFAULT 0,\
                                    lastID BIGINT NOT NULL DEFAULT 0,\
                                    niceColor VARCHAR(3) NOT NULL DEFAULT 'FFF',\
                                    niceColorRound INT NOT NULL DEFAULT 0,\
                                    niceColorCount BIGINT DEFAULT 0);\
               insert into game (seq) VALUES 0;\
               ")

cursor.execute("\
  USE CTF;\
    CREATE TABLE `data`(id INT NOT NULL,\
                         flags VARCHAR(255) NOT NULL,\
                         score INT NOT NULL,\
                         restrictions VARCHAR(255) NOT NULL,\
                         message_id BIGINT NOT NULL,\
                         case_status TINYINT(1) NOT NULL DEFAULT 0,\
                         start_time DATETIME NOT NULL,\
                         end_time DATETIME NOT NULL,\
                          title VARCHAR(255) NOT NULL,\
                          tried int NOT NULL DEFAULT 0,\
                         PRIMARY KEY(`id`)\
                         )\
    CREATE TABLE `history`\
    (data_id BIGINT ,\
      uid BIGINT NOT NULL,\
      count INT NOT NULL DEFAULT 0,\
        soived TINYINT(1) NOT NULL DEFAULT 0)\
      FOREIGN KEY (data_id) REFERENCES data(id)\
    );\
                  "
    )

print("done")
cursor.close()
connection.commit()
connection.close()