# Future statements
from __future__ import annotations

# Standard imports
import contextlib
import datetime
import types
import unittest
import unittest.mock

# Third-party imports
import discord

# Local imports
import uwu.cog.core.sql_abstract
import uwu.cog.daily_charge

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

    def test_is_forgivable(self) -> None:
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
                    uwu.cog.daily_charge.Charge.is_forgivable(
                        datetime.datetime.strptime(last_charge, "%Y-%m-%d %H:%M:%S")
                    )
                )

        for last_charge in test_cases_false:
            with self.subTest(last_charge=last_charge):
                self.assertFalse(
                    uwu.cog.daily_charge.Charge.is_forgivable(
                        datetime.datetime.strptime(last_charge, "%Y-%m-%d %H:%M:%S")
                    )
                )


class TestIsCrossDay(unittest.TestCase):
    def test_cross_day(self) -> None:
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
                    uwu.cog.daily_charge.Charge.is_cross_day(
                        datetime.datetime.strptime(last_charge, "%Y-%m-%d %H:%M:%S"),
                        datetime.datetime.strptime(executed_at, "%Y-%m-%d %H:%M:%S"),
                    )
                )

        for last_charge, executed_at in test_cases_false:
            with self.subTest(last_charge=last_charge, executed_at=executed_at):
                self.assertFalse(
                    uwu.cog.daily_charge.Charge.is_cross_day(
                        datetime.datetime.strptime(last_charge, "%Y-%m-%d %H:%M:%S"),
                        datetime.datetime.strptime(executed_at, "%Y-%m-%d %H:%M:%S"),
                    )
                )


class TestChargeResponse(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        bot = unittest.mock.Mock()
        self.charge = uwu.cog.daily_charge.Charge(bot)
        user = unittest.mock.Mock(spec=discord.User)
        user.id = 123
        user.name = "Test"
        user.avatar = None
        self.interaction = types.SimpleNamespace(
            user=user,
            channel=types.SimpleNamespace(id=456),
            guild_id=789,
            response=types.SimpleNamespace(
                defer=unittest.mock.AsyncMock(),
                send_message=unittest.mock.AsyncMock(),
            ),
            followup=types.SimpleNamespace(send=unittest.mock.AsyncMock()),
        )
        self.connection = unittest.mock.Mock()
        self.cursor = unittest.mock.Mock()
        self.state = {
            "last_charge": datetime.datetime.now().replace(microsecond=0)
            - datetime.timedelta(days=1),
            "charge_combo": 368,
            "point": 6451,
            "ticket": 16,
        }
        self.committed = self.state.copy()
        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)

        @contextlib.contextmanager
        def connection():
            # Regression: even a slow connection must start after defer.
            self.interaction.response.defer.assert_awaited()
            try:
                yield self.connection, self.cursor
            except Exception:
                self.state.update(self.committed)
                raise

        def commit():
            self.committed.update(self.state)

        self.connection.commit.side_effect = commit
        stack.enter_context(
            unittest.mock.patch.object(uwu.cog.core.sql, "mysql_connection", connection)
        )
        stack.enter_context(
            unittest.mock.patch.object(
                uwu.cog.core.sql,
                "read",
                side_effect=lambda uid, key, cursor: self.state[key],
            )
        )
        stack.enter_context(
            unittest.mock.patch.object(
                uwu.cog.core.sql,
                "write",
                side_effect=lambda uid, key, value, cursor: self.state.update(
                    {key: value}
                ),
            )
        )
        stack.enter_context(
            unittest.mock.patch.object(
                uwu.cog.daily_charge,
                "get_channels",
                return_value={"everyDayCharge": 456},
            )
        )
        stack.enter_context(
            unittest.mock.patch.object(self.charge, "is_forgivable", return_value=False)
        )
        stack.enter_context(
            unittest.mock.patch.object(
                self.charge, "embed_successful", return_value=discord.Embed()
            )
        )

    async def invoke(self) -> None:
        await uwu.cog.daily_charge.Charge.charge.callback(self.charge, self.interaction)

    async def test_success_acknowledges_before_database_and_uses_followup(self):
        await self.invoke()
        self.interaction.response.defer.assert_awaited_once_with()
        self.interaction.response.send_message.assert_not_awaited()
        self.interaction.followup.send.assert_awaited_once()
        self.assertEqual(self.committed["point"], 6456)
        self.assertEqual(self.committed["charge_combo"], 369)

    async def test_weekly_ticket_reward_is_not_duplicated_on_retry(self):
        self.state["charge_combo"] = 370
        await self.invoke()
        await self.invoke()
        self.assertEqual(self.committed["point"], 6456)
        self.assertEqual(self.committed["charge_combo"], 371)
        self.assertEqual(self.committed["ticket"], 20)

    async def test_failed_delivery_then_retry_does_not_reward_twice(self):
        self.interaction.followup.send.side_effect = RuntimeError("Discord unavailable")
        with self.assertRaisesRegex(RuntimeError, "Discord unavailable"):
            await self.invoke()
        committed = self.committed.copy()
        self.interaction.followup.send.side_effect = None
        await self.invoke()
        self.assertEqual(self.committed, committed)
        embed = self.interaction.followup.send.call_args.kwargs["embed"]
        self.assertIn("已入帳", embed.fields[0].value)

    async def test_already_charged_without_avatar_still_explains_result(self):
        self.state["last_charge"] = datetime.datetime.now().replace(microsecond=0)
        await self.invoke()
        self.connection.commit.assert_not_called()
        embed = self.interaction.followup.send.call_args.kwargs["embed"]
        self.assertIn("已記錄", embed.fields[0].value)

    async def test_wrong_channel_does_not_access_database(self):
        self.interaction.channel.id = 999
        await self.invoke()
        self.interaction.response.send_message.assert_awaited_once()
        self.interaction.response.defer.assert_not_awaited()
        self.interaction.followup.send.assert_not_awaited()


class TestDailyChargeIntegrationTest(unittest.TestCase):
    """
    There will be three Variable:

    ```
    is_forgivable: bool # sign before downtime and not loss combo
    ```
    """

    def test_panboyu3980(self) -> None:
        last_charge = datetime.datetime(2025, 3, 13, 9, 5, 0)
        is_forgivable = uwu.cog.daily_charge.Charge.is_forgivable(last_charge)
        self.assertTrue(is_forgivable)

        delta = uwu.cog.daily_charge.Charge.reward(
            user_or_uid=PANBOYU,
            last_charge=last_charge,
            executed_at=datetime.datetime(2025, 4, 12, 17, 26, 0),
            orig_combo=11,
            orig_point=1445,
            orig_ticket=4,
            is_forgivable=is_forgivable,
            testing=True,
        )
        expected = uwu.cog.core.sql_abstract.UserRecord(
            uid=PANBOYU,
            charge_combo=12,
            point=1450,
            last_charge=datetime.datetime(2025, 4, 12, 17, 26, 0),
        )
        self.assertEqual(delta, expected)

    def test_w4lnu7__(self) -> None:
        last_charge = datetime.datetime(2025, 3, 12, 21, 15, 0)
        is_forgivable = uwu.cog.daily_charge.Charge.is_forgivable(last_charge)
        self.assertFalse(is_forgivable)

        delta = uwu.cog.daily_charge.Charge.reward(
            user_or_uid=WALNUT,
            last_charge=last_charge,
            executed_at=datetime.datetime(2025, 4, 12, 20, 56, 0),
            orig_combo=24,
            orig_point=2564,
            orig_ticket=4,
            is_forgivable=is_forgivable,
            testing=True,
        )
        expected = uwu.cog.core.sql_abstract.UserRecord(
            uid=WALNUT,
            charge_combo=1,
            point=2569,
            last_charge=datetime.datetime(2025, 4, 12, 20, 56, 0),
        )
        self.assertEqual(delta, expected)

    def test_hatakutsu_yuevu(self) -> None:
        last_charge = datetime.datetime(2025, 4, 12, 16, 27, 0)
        is_forgivable = uwu.cog.daily_charge.Charge.is_forgivable(last_charge)
        self.assertFalse(is_forgivable)

        delta = uwu.cog.daily_charge.Charge.reward(
            user_or_uid=YUEVUWU,
            last_charge=last_charge,
            executed_at=datetime.datetime(2025, 4, 13, 2, 47, 0),
            orig_combo=2,
            orig_point=2751 - 5,
            orig_ticket=8,
            is_forgivable=is_forgivable,
            testing=True,
        )
        expected = uwu.cog.core.sql_abstract.UserRecord(
            uid=YUEVUWU,
            charge_combo=3,
            point=2751,
            last_charge=datetime.datetime(2025, 4, 13, 2, 47, 0),
        )
        self.assertEqual(delta, expected)


if __name__ == "__main__":
    unittest.main()
