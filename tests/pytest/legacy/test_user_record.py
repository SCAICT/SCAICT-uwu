# Standard imports
import unittest

# Third-party imports
import mysql.connector.errors

# Local imports
import cog.core.sql
import cog.core.sql_abstract

YUEVUWU = 545234619729969152

skip = False

try:
    with cog.core.sql.mysql_connection() as _:
        pass
except (RuntimeError, TypeError, mysql.connector.errors.Error):
    skip = True


class TestFromSQL(unittest.TestCase):
    @unittest.skipIf(skip, "Failed to connect to database.")
    def test_yuevuwu_exist(self):
        data = cog.core.sql_abstract.UserRecord.from_sql(YUEVUWU)
        self.assertIsNotNone(data)
        print(data)


if __name__ == "__main__":
    unittest.main()
