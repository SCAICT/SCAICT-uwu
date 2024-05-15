# Local imports
from .sql import link_sql
from .sql import end

# 初始化資料庫程式，從新增資料表開始

def create_ctf():
    connection, cursor = link_sql()
    cursor.execute("USE CTF") # 必須先去CREATE DATABASE CTF

    cursor.execute('\
        CREATE TABLE data (\
            id BIGINT PRIMARY KEY,\
            flags VARCHAR(255),\
            score INT,\
            restrictions VARCHAR(255),\
            message_id BIGINT,\
            case_status BOOLEAN,\
            start_time DATETIME,\
            end_time VARCHAR(255),\
            title VARCHAR(255),\
            tried INT\
        );\
\
        CREATE TABLE history (\
            data_id BIGINT,\
            uid BIGINT,\
            count INT,\
            solved TINYINT(1) NOT NULL DEFFALT 0,\
            FOREIGN KEY (data_id) REFERENCES data(id) ON DELETE CASCADE\
        );\
    ')

    end(connection, cursor)
