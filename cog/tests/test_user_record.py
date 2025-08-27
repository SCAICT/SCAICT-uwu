import unittest

from mysql.connector.errors import Error as MySQLError

from cog.core.sql import mysql_connection
from cog.core.sql_abstract import UserRecord


YUEVUWU = 545234619729969152

SKIP = False
try:
    with mysql_connection() as _:
        pass
except (RuntimeError, MySQLError, TypeError):
    SKIP = True


class TestFromSQL(unittest.TestCase):
    @unittest.skipIf(SKIP, "Failed to connect to database.")
    def test_yuevuwu_exist(self):
        data = UserRecord.from_sql(YUEVUWU)
        self.assertIsNotNone(data)
        print(data)


if __name__ == "__main__":
    unittest.main()
