import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv(f'{os.getcwd()}/.env')


HOSTIP = os.getenv('HOST')
PORT= os.getenv('MYSQL_PORT')
DBUSER = os.getenv('MYSQL_USER')
DBNAME= os.getenv('MYSQL_DATABASE')
PWD = os.getenv('MYSQL_PASSWORD')
def connect():
    connection = mysql.connector.connect(host=HOSTIP,
                                        port=PORT,
                                        user=DBUSER,
                                        passwd=PWD,
                                        database=DBNAME
    )

    return connection
