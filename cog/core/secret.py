# Future statements
from __future__ import annotations

# Standard imports
import os

# Third-party imports
import dotenv
import mysql.connector
import mysql.connector.abstracts
import mysql.connector.pooling

dotenv.load_dotenv(f"{os.getcwd()}/.env")

DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_NAME = os.getenv("MYSQL_DATABASE")
DB_HOST = os.getenv("HOST")
DB_PORT = os.getenv("MYSQL_PORT")


def connect() -> (
    mysql.connector.pooling.PooledMySQLConnection
    | mysql.connector.abstracts.MySQLConnectionAbstract
):
    """
    Returns:
        mysql.connector.pooling.PooledMySQLConnection | mysql.connector.abstracts.MySQLConnectionAbstract:
    """

    return mysql.connector.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT,
    )
