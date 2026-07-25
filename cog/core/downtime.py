# Future statements
from __future__ import annotations

# Standard imports
import dataclasses
import datetime
import json
import os
import typing

# Third-party imports
import discord
import discord.abc

# Local imports
import cog.core.safe_write

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S%z"
DOWNTIME_PATH = f"{os.getcwd()}/DataBase/downtime.json"


@dataclasses.dataclass
class Downtime:
    start: datetime.datetime
    # TODO: will Downtime.end be None?
    end: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.now)
    is_restored: bool = False

    def __post_init__(self) -> None:
        if self.end.tzinfo is None:
            self.end = self.end.astimezone()

    def __contains__(self, timestamp: datetime.datetime) -> bool:
        """
        Parameters:
            timestamp (datetime.datetime):

        Returns:
            bool:
        """

        if self.end.tzinfo is None:  # XXX: True when self.end is set after init
            self.end = self.end.astimezone()

        return self.start <= timestamp <= self.end

    @staticmethod
    def from_str(
        start_str: str, end_str: str | None = None, is_restored: bool = False
    ) -> Downtime:
        """
        Parameters:
            start_str (str):
            end_str (str | None):
            is_restored (bool):

        Returns:
            cog.core.downtime.Downtime:
        """

        start = datetime.datetime.strptime(start_str, DATETIME_FORMAT)

        if end_str:
            end = datetime.datetime.strptime(end_str, DATETIME_FORMAT)
        else:
            end = datetime.datetime.now()

        return Downtime(start, end, is_restored)

    @staticmethod
    def from_dict(d: dict) -> Downtime:
        """
        Parameters:
            d (dict):

        Returns:
            cog.core.downtime.Downtime:
        """

        return Downtime.from_str(
            start_str=d["start"],
            end_str=d.get("end", None),
            is_restored=d.get("is_restored", False),
        )

    def to_dict(self) -> dict[str, str | bool]:
        """
        Returns:
            dict[str, str | bool]:
        """

        return {
            "start": datetime.datetime.strftime(self.start, DATETIME_FORMAT),
            "end": datetime.datetime.strftime(self.end, DATETIME_FORMAT),
            "is_restored": self.is_restored,
        }

    def marked_as_restored(self) -> typing.Self:
        """
        Returns:
            typing.Self:
        """

        self.is_restored = True

        return self


def get_downtime_list() -> list[Downtime]:
    """
    Returns:
        list[cog.core.downtime.Downtime]:
    """

    with open(DOWNTIME_PATH, "r", encoding="utf-8") as file:
        data: list[dict[str, str | bool]] = json.load(file)

    return list(map(Downtime.from_dict, data))


def write_downtime_list(downtime_list: list[Downtime]) -> None:
    """
    Parameters:
        downtime_list (list[cog.core.downtime.Downtime]):
    """

    with cog.core.safe_write.safe_open_w(DOWNTIME_PATH, encoding="utf-8") as file:
        json.dump([downtime.to_dict() for downtime in downtime_list], file, indent=4)


async def get_history(
    bot: discord.Bot,
    channel_id,
    *,
    after: datetime.datetime,
    before: datetime.datetime | None = None,
) -> list[discord.Message]:
    """
    Parameters:
        bot (discord.Bot):
        channel_id:
        after (datetime.datetime:
        before (datetime.datetime | None):

    Returns:
        list[discord.Message]:

    Raises:
        ValueError:
    """

    if before is None:
        before = datetime.datetime.now()

    channel: discord.abc.Messageable = bot.get_channel(channel_id)

    if not channel:
        raise ValueError(f"Cannot get channel (id={channel}).")

    if not isinstance(channel, discord.abc.Messageable):
        raise ValueError(
            f"{channel.name} (id={channel_id}, type={type(channel)}) is not messageable."
        )

    # if datetime is naive, it is assumed to be local time
    messages = await channel.history(
        limit=None, after=after, before=before, oldest_first=True
    ).flatten()

    return messages
