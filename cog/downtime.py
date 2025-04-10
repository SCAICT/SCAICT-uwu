from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import os

DATETIME_FORMAT = "%y-%m-%d %H:%M:%S"
DOWNTIME_PATH = f"{os.getcwd()}/DataBase/downtime.json"


@dataclass
class Downtime:
    start: datetime
    # TODO: will Downtime.end be None?
    end: datetime = datetime.now()
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
    def from_dict(d: dict[str, str | bool]):
        return (
            Downtime.from_str(
                start_str=str(d["start"]),
                end_str=str(d.get("end", None)),
                is_restored=bool(d.get("is_restored", False)),
            ),
        )

    def to_dict(self) -> dict[str, str | bool]:
        return self.__dict__

    def marked_as_restored(self) -> Downtime:
        self.is_restored = True
        return self


def get_downtime_list() -> list[Downtime]:
    with open(DOWNTIME_PATH, "r", encoding="utf-8") as file:
        data: list[dict[str, str | bool]] = json.load(file)

    return list(*map(Downtime.from_dict, data))


def write_downtime_list(downtime_list: list[Downtime]):
    with open(DOWNTIME_PATH, "w", encoding="utf-8") as file:
        json.dump([downtime.to_dict() for downtime in downtime_list], file, indent=4)
