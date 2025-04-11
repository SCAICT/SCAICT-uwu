from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import json
import os

from discord import Bot
from discord.abc import Messageable

from cog.core.safe_write import safe_open_w

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DOWNTIME_PATH = f"{os.getcwd()}/DataBase/downtime.json"


@dataclass
class Downtime:
    start: datetime
    # TODO: will Downtime.end be None?
    end: datetime = field(default_factory=datetime.now)
    is_restored: bool = False

    def __contains__(self, timestamp: datetime):
        start = self.start
        end = self.end or datetime.now()
        return start <= timestamp <= end

    @staticmethod
    def from_str(
        start_str: str, end_str: str | None = None, is_restored=False
    ) -> Downtime:
        start = datetime.strptime(start_str, DATETIME_FORMAT)
        if end_str:
            end = datetime.strptime(end_str, DATETIME_FORMAT)
        else:
            end = datetime.now()
        return Downtime(start, end, is_restored)

    @staticmethod
    def from_dict(d: dict) -> Downtime:
        return Downtime.from_str(
            start_str=d["start"],
            end_str=d.get("end", None),
            is_restored=d.get("is_restored", False),
        )

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "start": datetime.strftime(self.start, DATETIME_FORMAT),
            "end": datetime.strftime(self.end, DATETIME_FORMAT),
            "is_restored": self.is_restored,
        }

    def marked_as_restored(self) -> Downtime:
        self.is_restored = True
        return self


def get_downtime_list() -> list[Downtime]:
    with open(DOWNTIME_PATH, "r", encoding="utf-8") as file:
        data: list[dict[str, str | bool]] = json.load(file)

    return list(map(Downtime.from_dict, data))


def write_downtime_list(downtime_list: list[Downtime]):
    with safe_open_w(DOWNTIME_PATH, encoding="utf-8") as file:
        json.dump([downtime.to_dict() for downtime in downtime_list], file, indent=4)


async def get_history(
    bot: Bot, channel_id, *, after: datetime, before: datetime | None = None
):
    if before is None:
        before = datetime.now()
    channel: Messageable = bot.get_channel(channel_id)

    if not channel:
        raise ValueError(f"Cannot get channel (id={channel}).")

    if not isinstance(channel, Messageable):
        raise ValueError(
            f"{channel.name} (id={channel_id}, type={type(channel)}) is not messageable."
        )

    messages = await channel.history(
        limit=None, after=after, before=before, oldest_first=True
    ).flatten()

    return messages
