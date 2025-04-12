import unittest
from datetime import datetime

from ..daily_charge import Charge
from ..core.sql_abstract import UserRecord

YUEVUWU = 1
PANBOYU = 2
WALNUT = 3


# TODO: specify downtime_list with argument
class TestIsForgivable(unittest.TestCase):
    # downtime_list = [
    #     {
    #         "start": "2025-03-14 09:03:00+0800",
    #         "end": "2025-04-12 16:26:35+0800",
    #         "is_restored": true
    #     }
    # ]

    def test_is_forgivable(self):
        test_cases_true = [
            "2025-03-13 00:00:00",
            "2025-03-13 23:59:59",
            "2025-03-14 00:00:00",
            "2025-03-14 23:59:59",
        ]

        test_cases_false = [
            "2025-03-12 23:59:59",
            "2025-03-15 00:00:00",
        ]

        for last_charge in test_cases_true:
            with self.subTest(last_charge=last_charge):
                self.assertTrue(
                    Charge.is_forgivable(
                        datetime.strptime(last_charge, "%Y-%m-%d %H:%M:%S")
                    )
                )
        for last_charge in test_cases_false:
            with self.subTest(last_charge=last_charge):
                self.assertFalse(
                    Charge.is_forgivable(
                        datetime.strptime(last_charge, "%Y-%m-%d %H:%M:%S")
                    )
                )


class TestIsCrossDay(unittest.TestCase):
    def test_cross_day(self):
        test_cases_true = [
            ("2024-01-01 01:00:00", "2024-01-03 00:00:00"),
            ("2024-01-01 01:00:00", "2024-01-03 00:59:59"),
            ("2024-01-01 01:00:00", "2024-01-03 01:00:00"),
        ]
        test_cases_false = [
            ("2024-01-01 01:00:00", "2024-01-02 10:10:00"),
            ("2024-01-01 01:00:00", "2024-01-02 01:00:00"),
            ("2024-01-01 01:00:00", "2024-01-02 23:59:59"),
        ]

        for last_charge, executed_at in test_cases_true:
            with self.subTest(last_charge=last_charge, executed_at=executed_at):
                self.assertTrue(
                    Charge.is_cross_day(
                        datetime.strptime(last_charge, "%Y-%m-%d %H:%M:%S"),
                        datetime.strptime(executed_at, "%Y-%m-%d %H:%M:%S"),
                    )
                )
        for last_charge, executed_at in test_cases_false:
            with self.subTest(last_charge=last_charge, now=executed_at):
                self.assertFalse(
                    Charge.is_cross_day(
                        datetime.strptime(last_charge, "%Y-%m-%d %H:%M:%S"),
                        datetime.strptime(executed_at, "%Y-%m-%d %H:%M:%S"),
                    )
                )


class TestDailyChargeIntegrationTest(unittest.TestCase):
    """
    There will be three Variable:
    ```
    is_forgivable: bool # sign before downtime and not loss combo
    ```
    """

    def test_panboyu3980(self):
        last_charge = datetime(2025, 3, 13, 9, 5, 0)
        is_forgivable = Charge.is_forgivable(last_charge)
        self.assertTrue(is_forgivable)

        delta = Charge.reward(
            user_or_uid=PANBOYU,
            last_charge=last_charge,
            executed_at=datetime(2025, 4, 12, 17, 26, 0),
            orig_combo=11,
            orig_point=1445,
            orig_ticket=4,
            is_forgivable=is_forgivable,
            testing=True,
        )
        expected = UserRecord(
            uid=PANBOYU,
            charge_combo=12,
            point=1450,
            last_charge=datetime(2025, 4, 12, 17, 26, 0),
        )
        self.assertEqual(delta, expected)

    def test_w4lnu7__(self):
        last_charge = datetime(2025, 3, 12, 21, 15, 0)
        is_forgivable = Charge.is_forgivable(last_charge)
        self.assertFalse(is_forgivable)

        delta = Charge.reward(
            user_or_uid=WALNUT,
            last_charge=last_charge,
            executed_at=datetime(2025, 4, 12, 20, 56, 0),
            orig_combo=24,
            orig_point=2564,
            orig_ticket=4,
            is_forgivable=is_forgivable,
            testing=True,
        )
        expected = UserRecord(
            uid=WALNUT,
            charge_combo=1,
            point=2569,
            last_charge=datetime(2025, 4, 12, 20, 56, 0),
        )
        self.assertEqual(delta, expected)

    def test_hatakutsu_yuevu(self):
        last_charge = datetime(2025, 4, 12, 16, 27, 0)
        is_forgivable = Charge.is_forgivable(last_charge)
        self.assertFalse(is_forgivable)

        delta = Charge.reward(
            user_or_uid=YUEVUWU,
            last_charge=last_charge,
            executed_at=datetime(2025, 4, 13, 2, 47, 0),
            orig_combo=2,
            orig_point=2751 - 5,
            orig_ticket=8,
            is_forgivable=is_forgivable,
            testing=True,
        )
        expected = UserRecord(
            uid=YUEVUWU,
            charge_combo=3,
            point=2751,
            last_charge=datetime(2025, 4, 13, 2, 47, 0),
        )
        self.assertEqual(delta, expected)


if __name__ == "__main__":
    unittest.main()
