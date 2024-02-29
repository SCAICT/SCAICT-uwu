import mysql.connector
def connect():
    connection = mysql.connector.connect(host="",
                                        port="",
                                        user="",  
                                        passwd="",
                                        database=""
    )
    return connection