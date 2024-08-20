"""
FIXME: Database table gift was missing here. See admin_role.py
"""

# Third-party imports
# import mysql.connector

# Local imports
from .sql import link_sql

connection, cursor = link_sql()

# Use your database instead
cursor.execute("USE dcsqltest")

cursor.execute("\
    CREATE TABLE `user` (\
        uid BIGINT NOT NULL,\
        loveuwu TINYINT(1) NOT NULL DEFAULT 0,\
        point INT NOT NULL DEFAULT 0,\
        ticket INT NOT NULL DEFAULT 0,\
        charge_combo INT NOT NULL DEFAULT 0,\
        next_lottery INT NOT NULL DEFAULT 0,\
        last_charge DATETIME NOT NULL DEFAULT '1970-01-01 00:00:00',\
        last_comment DATE NOT NULL DEFAULT '1970-01-01',\
        today_comments INT NOT NULL DEFAULT 0,\
        PRIMARY KEY (`uid`)\
    )\
")

cursor.execute("\
    CREATE TABLE `commentpoints` (\
        seq INT AUTO_INCREMENT PRIMARY KEY,\
        uid BIGINT NOT NULL,\
        times INT NOT NULL DEFAULT 2,\
        next_reward INT NOT NULL DEFAULT 1,\
        FOREIGN KEY (`uid`) REFERENCES USER(`uid`) ON DELETE CASCADE\
    )\
")

cursor.execute("\
    CREATE TABLE `game` (\
        seq BIGINT NOT NULL DEFAULT 0,\
        lastid BIGINT NOT NULL DEFAULT 0,\
        nicecolor VARCHAR(3) NOT NULL DEFAULT 'FFF',\
        nicecolorround INT NOT NULL DEFAULT 0,\
        nicecolorcount BIGINT DEFAULT 0\
    );\
    insert into game (seq) VALUES 0;\
")

cursor.execute("\
    USE ctf;\
    CREATE TABLE `data` (\
        id INT NOT NULL,\
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
    CREATE TABLE `history` (\
        data_id BIGINT,\
        uid BIGINT NOT NULL,\
        count INT NOT NULL DEFAULT 0,\
        soived TINYINT(1) NOT NULL DEFAULT 0\
    )\
    FOREIGN KEY (data_id) REFERENCES data(id)\
    );\
")

# 查看所有database
# cursor.execute("SHOW DATABASES")
# ret = cursor.fetchall()
# print(ret)

print("done")
cursor.close()
connection.commit()
connection.close()
