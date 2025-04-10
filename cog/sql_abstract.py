from __future__ import annotations
from abc import ABC, abstractmethod
from collections import UserDict
from datetime import datetime, date
from dataclasses import dataclass, is_dataclass, fields
from typing import Generic, TypeVar

from cog.core.sql import fetchone_by_primary_key, write, mysql_connection
from cog.singleton import SingletonMeta


# TODO: extend if we need to judge the unset value is nullable
class UnsetSentinel(metaclass=SingletonMeta):
    def __repr__(self):
        return "UNSET"


UNSET = UnsetSentinel()


class Unsettable:
    def __getattribute__(self, name):
        value = super().__getattribute__(name)
        if value is UNSET:
            raise UnsetError(f"Attribute '{name}' is not set")

    def is_unset(self, attr_name):
        return super().__getattribute__(attr_name) == UNSET


class UnsetError(Exception):
    pass


DataclassT = TypeVar("DataclassT")


# TODO: optimize with attr module
class AttributeKeyedDict(UserDict, Generic[DataclassT]):
    def __init__(self, primary_key_name: str, *args, **kwargs):
        if not is_dataclass(DataclassT):
            raise TypeError(
                "KeyedDict should be specified a dataclass as the type of the item."
            )

        if not primary_key_name in DataclassT.__annotations__:
            raise AttributeError(
                f"The field `{primary_key_name}` is not announced in the dataclass {DataclassT}"
            )

        self.primary_key_name = primary_key_name
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, item: DataclassT):
        raise RuntimeError("Please use `set()` method to set records")

    def set(self, record: DataclassT):
        identifier = getattr(record, self.primary_key_name)
        return super().__setitem__(identifier, record)


def is_protected_name(name: str) -> bool:
    return name.startswith("_") and not name.startswith("__")


class ProtectedAttrReadOnlyMixin:
    def __setattr__(self, name: str, value):
        is_protected = is_protected_name(name)
        is_set = name in self.__dict__
        if is_protected and is_set:
            raise AttributeError(
                f"The protected attribute `{name}` should be read-only after initialization."
            )
        return super().__setattr__(name, value)


class SQLTable(ABC):
    @abstractmethod
    @staticmethod
    def from_sql(unique_id): ...

    @abstractmethod
    def to_sql(self): ...


@dataclass
class UserRecord(SQLTable, Unsettable, ProtectedAttrReadOnlyMixin):
    uid: int  # required

    DCname: str | None = UNSET  # pyright: ignore[reportAssignmentType]
    DCMail: str | None = UNSET  # pyright: ignore[reportAssignmentType]
    githubName: str | None = UNSET  # pyright: ignore[reportAssignmentType]
    githubMail: str | None = UNSET  # pyright: ignore[reportAssignmentType]
    loveuwu: bool = UNSET  # pyright: ignore[reportAssignmentType]
    point: int = UNSET  # pyright: ignore[reportAssignmentType]
    ticket: int = UNSET  # pyright: ignore[reportAssignmentType]
    charge_combo: int = UNSET  # pyright: ignore[reportAssignmentType]
    next_lottery: int = UNSET  # pyright: ignore[reportAssignmentType]
    last_charge: datetime = UNSET  # pyright: ignore[reportAssignmentType]
    last_comment: date = UNSET  # pyright: ignore[reportAssignmentType]
    today_comments: int = UNSET  # pyright: ignore[reportAssignmentType]
    admkey: str | None = UNSET  # pyright: ignore[reportAssignmentType]

    _protected: bool = False  # readonly after init

    # won't place default value unless use default() to ensure safety
    @staticmethod
    def default(uid):
        return UserRecord(
            uid=uid,
            DCname=None,
            DCMail=None,
            githubName=None,
            githubMail=None,
            loveuwu=False,
            point=0,
            ticket=1,
            charge_combo=0,
            next_lottery=0,
            last_charge=datetime(1970, 1, 1, 0, 0, 0),
            last_comment=date(1970, 1, 1),
            today_comments=0,
            admkey=None,
        )

    @staticmethod
    def from_sql(  # pylint: disable=arguments-renamed # pyright: ignore[reportIncompatibleMethodOverride]
        uid: int,
    ):

        data = fetchone_by_primary_key("user", "uid", uid)
        if data is None:
            return None

        record = UserRecord(
            _protected=True, **data  # pyright: ignore[reportArgumentType]
        )

        assert any(
            record.is_unset(field.name) for field in fields(record)
        ), "SQL is not return all fields"

        return record

    def to_sql(self):
        if self._protected:
            raise ValueError("You should new a object to modify.")
        self.to_sql_unsafe()

    def to_sql_unsafe(self):
        with mysql_connection() as cursor:
            for field in fields(self):
                if field.name.startswith("_"):  # _protected
                    continue

                try:
                    # only write changed value by check if value is unset or not
                    value = getattr(self, field.name)
                    write(self.uid, field.name, value, cursor)
                except UnsetError:
                    continue
        #         except MySQLError:
        #             False

        # return True


class UserRecordDict(AttributeKeyedDict[UserRecord]):
    def __init__(self):
        super().__init__("uid")
