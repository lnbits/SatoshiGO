from quart import g, abort, render_template, websocket, jsonify
from http import HTTPStatus
import pyqrcode
from io import BytesIO
from lnbits.decorators import check_user_exists, validate_uuids

from . import satoshigo_ext
from .crud import get_satoshigo_game
from functools import wraps
import trio


@satoshigo_ext.route("/")
@validate_uuids(["usr"], required=True)
@check_user_exists()
async def index():
    return await render_template("satoshigo/index.html", user=g.user)


@satoshigo_ext.route("/test/")
async def test():
    return await render_template("satoshigo/testleaflet.html")


@satoshigo_ext.route("/<game_id>")
async def display(game_id):
    game = await get_satoshigo_game(game_id) or abort(
        HTTPStatus.NOT_FOUND, "satoshigo game does not exist."
    )
    return await render_template(
        "satoshigo/display.html",
        totalFunds=game.totalFunds,
        fundsCollected=game.fundsCollected,
        game_id=game_id,
    )


##################WEBSOCKET ROUTES########################

# socket_relay is a list where the control panel or
# lnurl endpoints can leave a message for the compose window

connected_websockets = set()


def collect_websocket(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        global connected_websockets
        send_channel, receive_channel = trio.open_memory_channel(0)
        connected_websockets.add(send_channel)
        try:
            return await func(receive_channel, *args, **kwargs)
        finally:
            connected_websockets.remove(send_channel)

    return wrapper


@satoshigo_ext.websocket("/ws")
@collect_websocket
async def wss(receive_channel):
    while True:
        data = await receive_channel.receive()
        await websocket.send(data)


async def broadcast(message):
    print(connected_websockets)
    for queue in connected_websockets:
        await queue.send(f"{message}")
