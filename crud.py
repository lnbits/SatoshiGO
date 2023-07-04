import random
from datetime import datetime
from typing import List, Optional, Union
from lnbits.helpers import urlsafe_short_hash
import json
import sqlite3
import math
from . import db
from .models import (
    satoshigoGame,
    satoshigoFunding,
    satoshigoPlayers,
    satoshigoAreas,
    satoshigoItems,
)

from lnbits.core.crud import (
    create_account,
    get_user,
    get_payments,
    create_wallet,
    delete_wallet,
)


async def create_satoshigo_game(
    *,
    wallet: str,
    wallet_key: str,
    title: str,
    description: str,
) -> satoshigoGame:
    game_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO satoshigo_game (
            hash,
            title,
            description,
            area,
            appearance,
            isDefault,
            flags,
            totalFunds,
            fundsCollected,
            wallet,
            wallet_key
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (game_id, title, description, "", "", True, 0, 0, 0, wallet, wallet_key),
    )
    game = await get_satoshigo_game(game_id)
    assert game, "Newly created game couldn't be retrieved"
    return game


async def get_satoshigo_game(game_id: str) -> Optional[satoshigoGame]:
    row = await db.fetchone("SELECT * FROM satoshigo_game WHERE hash = ?", (game_id,))
    return satoshigoGame._make(row)


async def get_satoshigo_games() -> List[satoshigoGame]:

    rows = await db.fetchall(
        "SELECT * FROM satoshigo_game",
    )
    return [satoshigoGame.from_row(row) for row in rows]


async def get_satoshigo_admin_games(
    wallet_ids: Union[str, List[str]]
) -> List[satoshigoGame]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(
        f"SELECT * FROM satoshigo_game WHERE wallet IN ({q})", (*wallet_ids,)
    )
    return [satoshigoGame.from_row(row) for row in rows]


async def update_satoshigo_game(game_id: str, **kwargs) -> Optional[satoshigoGame]:
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    await db.execute(
        f"UPDATE satoshigo_game SET {q} WHERE hash = ?", (*kwargs.values(), game_id)
    )
    row = await db.fetchone("SELECT * FROM satoshigo_game WHERE hash = ?", (game_id,))
    return satoshigoGame.from_row(row) if row else None


async def delete_satoshigo_game(game_id: str) -> None:
    await db.execute("DELETE FROM satoshigo_game WHERE hash = ?", (game_id,))


################################## FUNDING


async def create_satoshigo_funding(
    *,
    game_id: str,
    wallet: str,
    tplat: int,
    tplon: int,
    btlat: int,
    btlon: int,
    amount: int,
    payment_hash: str,
) -> satoshigoGame:
    funding_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO satoshigo_funding (
            id,
            satoshigo_id,
            wallet,
            tplat,
            tplon,
            btlat,
            btlon,
            amount,
            payment_hash,
            confirmed
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            funding_id,
            game_id,
            wallet,
            tplat,
            tplon,
            btlat,
            btlon,
            amount,
            payment_hash,
            False,
        ),
    )
    funding = await get_satoshigo_funding(payment_hash)
    assert funding, "Newly created funding couldn't be retrieved"
    return funding


async def get_satoshigo_funding(payment_hash: str) -> Optional[satoshigoFunding]:
    row = await db.fetchone(
        "SELECT * FROM satoshigo_funding WHERE payment_hash = ?", (payment_hash,)
    )
    return satoshigoFunding._make(row)


async def get_satoshigo_fundings(game_id: str) -> Optional[satoshigoFunding]:
    row = await db.fetchall(
        "SELECT * FROM satoshigo_funding WHERE game_id = ?", (game_id,)
    )
    return satoshigoFunding._make(row)


async def update_satoshigo_funding(
    payment_hash: str, **kwargs
) -> Optional[satoshigoFunding]:
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    await db.execute(
        f"UPDATE satoshigo_funding SET {q} WHERE payment_hash = ?",
        (*kwargs.values(), payment_hash),
    )
    row = await db.fetchone(
        "SELECT * FROM satoshigo_funding WHERE payment_hash = ?", (payment_hash,)
    )
    return satoshigoFunding._make(row)


###########################PLAYER


async def create_satoshigo_player(user_name: str):
    account = await create_account()
    user = await get_user(account.id)
    assert user, "Newly created user couldn't be retrieved"

    wallet = await create_wallet(user_id=user.id, wallet_name="satsgo")

    await db.execute(
        """
        INSERT INTO satoshigo_players (id, user_name, adminkey, inkey, gameHash, enableHiScore)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user.id, user_name, wallet.adminkey, wallet.inkey, "", False),
    )
    player = await get_satoshigo_player(user.id)
    return player


async def update_satoshigo_player(user_id: str, **kwargs) -> Optional[satoshigoPlayers]:
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    await db.execute(
        f"UPDATE satoshigo_players SET {q} WHERE id = ?", (*kwargs.values(), user_id)
    )
    row = await db.fetchone("SELECT * FROM satoshigo_players WHERE id = ?", (user_id,))
    return satoshigoPlayers.from_row(row) if row else None


async def get_satoshigo_player(user_id: str) -> Optional[satoshigoPlayers]:
    row = await db.fetchone("SELECT * FROM satoshigo_players WHERE id = ?", (user_id,))
    return satoshigoPlayers._make(row)


async def get_satoshigo_player_gameid(game_id: str) -> Optional[satoshigoPlayers]:
    rows = await db.fetchall(
        "SELECT * FROM satoshigo_players WHERE gameHash = ?", (game_id,)
    )
    return [satoshigoPlayers._make(row) for row in rows]


async def get_satoshigo_player_inkey(inkey: str) -> Optional[satoshigoPlayers]:
    row = await db.fetchone("SELECT * FROM satoshigo_players WHERE inkey = ?", (inkey,))
    return row


#########cAREAS


async def create_area(lon: float, lat: float, radius: int, gameHash: str):
    area_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO satoshigo_areas (hash, lon, lat, radius, gameHash)
        VALUES (?, ?, ?, ?, ?)
        """,
        (area_id, lon, lat, radius, gameHash),
    )
    return area_id


async def get_satoshigo_areas(
    lon: float, lat: float, radius: int, exclude: str
) -> Optional[satoshigoAreas]:

    R = 6378137
    dLat = (radius / 2) / R
    dLon = (radius / 2) / (R * math.cos(math.pi * lat / 180))

    latO = lat + dLat * 180 / math.pi
    lonO = lon + dLon * 180 / math.pi
    lat1 = lat - dLat * 180 / math.pi
    lon1 = lon - dLon * 180 / math.pi

    rows = await db.fetchall(
        """
        SELECT * FROM satoshigo_areas WHERE 
        lat >= ? AND lat <= ? AND lon >= ? AND lon <= ?
        
        """,
        (lat1, latO, lon1, lonO),
    )
    return [satoshigoAreas._make(row) for row in rows]


async def get_satoshigo_area(area_id: str) -> Optional[satoshigoAreas]:
    row = await db.fetchone("SELECT * FROM satoshigo_areas WHERE hash = ?", (area_id,))
    return satoshigoAreas._make(row)


async def get_satoshigo_delete_area(area_id: str) -> None:
    await db.execute("DELETE FROM satoshigo_areas WHERE hash = ?", (area_id,))


###########################ITEMS


async def create_satoshigo_item(type: str, areaHash: str, data: int, appearance: str):
    hash = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO satoshigo_items (hash, type, areaHash, data, appearance)
        VALUES (?, ?, ?, ?, ?)
        """,
        (hash, type, areaHash, data, appearance),
    )
    item = await get_satoshigo_item(hash)
    return item


async def update_satoshigo_item(item_id: str, **kwargs) -> Optional[satoshigoItems]:
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    await db.execute(
        f"UPDATE satoshigo_items SET {q} WHERE id = ?", (*kwargs.values(), item_id)
    )
    row = await db.fetchone("SELECT * FROM satoshigo_items WHERE hash = ?", (item_id,))
    return satoshigoItems.from_row(row) if row else None


async def get_satoshigo_item(item_id: str) -> Optional[satoshigoItems]:
    row = await db.fetchone("SELECT * FROM satoshigo_items WHERE hash = ?", (item_id,))
    return satoshigoItems._make(row)


async def delete_satoshigo_item(item_id: str) -> None:
    await db.execute("DELETE FROM satoshigo_items WHERE hash = ?", (item_id,))


async def get_satoshigo_items(area_id: str) -> Optional[satoshigoItems]:
    rows = await db.fetchall(
        "SELECT * FROM satoshigo_items WHERE areaHash = ?", (area_id,)
    )
    return [satoshigoItems._make(row) for row in rows]
