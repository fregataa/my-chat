import logging

from aiohttp import web, WSMsgType

logger = logging.getLogger('mychat.server')
logging.basicConfig(level=logging.INFO)

async def index(request):
    ws_current = web.WebSocketResponse()

    await ws_current.prepare(request)

    name = request.match_info['username']
    logger.info('%s joined.', name)

    await ws_current.send_json({'action': 'connect', 'name': name})

    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'join', 'name': name})
    request.app['websockets'][name] = ws_current

    while True:
        msg = await ws_current.receive()

        if msg.type == WSMsgType.text:
            for ws in request.app['websockets'].values():
                if ws is not ws_current:
                    await ws.send_json(
                        {'action': 'sent', 'name': name, 'text': msg.data})
        else:
            break

    del request.app['websockets'][name]
    logger.info('%s disconnected.', name)
    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'disconnect', 'name': name})

    return ws_current
