from quart import url_for
from sqlite3 import Row
from typing import NamedTuple
import shortuuid  # type: ignore


class satoshigoFunding(NamedTuple):
    id: str
    satoshigo_id: str
    wallet: str
    tplat: int
    tplon: int
    btlat: int
    btlon: int
    amount: int
    payment_hash: str
    confirmed: bool
    time: int

    @classmethod
    def from_row(cls, row: Row) -> "satoshigoFunding":
        return cls(**dict(row))


class satoshigoGame(NamedTuple):
    hash: str
    title: str
    description: str
    area: str
    appearance: str
    isDefault: int
    flags: int
    totalFunds: int
    fundsCollected: int
    wallet: str
    wallet_key: str

    @classmethod
    def from_row(cls, row: Row) -> "satoshigoGame":
        return cls(**dict(row))


class satoshigoPlayers(NamedTuple):
    id: str
    user_name: str
    adminkey: str
    inkey: str
    gameHash: str
    enableHiScore: int

    @classmethod
    def from_row(cls, row: Row) -> "satoshigoPlayers":
        return cls(**dict(row))


class satoshigoAreas(NamedTuple):
    hash: str
    lon: int
    lat: int
    radius: int
    gameHash: str
    time: str

    @classmethod
    def from_row(cls, row: Row) -> "satoshigoAreas":
        return cls(**dict(row))


class satoshigoItems(NamedTuple):
    hash: str
    type: str
    areaHash: str
    data: int
    appearance: str

    @classmethod
    def from_row(cls, row: Row) -> "satoshigoItems":
        return cls(**dict(row))
