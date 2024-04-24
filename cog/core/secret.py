# IMPORTANT!!!!Must ignore git!!!
import mysql.connector

def connect():
    connection = mysql.connector.connect(
        host = "",
        port = "",
        user = "",
        passwd = "",
        database = "",
        auth_plugin = "mysql_native_password"
    )
    return connection
