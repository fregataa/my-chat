
import logging
import json
import asyncio

from aiohttp import web, WSMsgType
from aioredis import from_url as get_redis
from aioredis.utils import str_if_bytes

logger = logging.getLogger('mychat.server')
logging.basicConfig(level=logging.INFO)

WS_IO = None


class InvalidCommand(web.HTTPBadRequest):
    reason = 'Invalid type of command'

async def get_msg(ws_current, request, redis, send_data):
    while True:
        try:
            msg = await ws_current.receive(timeout=0.1)
            logger.info(f"\n========\nmessage from ws: {msg}")
        except asyncio.TimeoutError:
            await asyncio.sleep(0)
        else:
            if msg.type == WSMsgType.text:
                    for ws in request.app['websockets'].values():
                        if ws is ws_current:
                            data = json.dumps({**send_data, 'text': msg.data})
                            await redis.publish('channel:1', data)
            else:
                break

async def subscribe(ws_current, redis):
    pubsub = redis.pubsub()
    async with pubsub as p:
        await p.subscribe('channel:1')
        while True:
            try:
                res = await p.parse_response(timeout=0.1)
                logger.info(f"\n========\nresponse from redis: {res}")
            except asyncio.TimeoutError:
                await asyncio.sleep(0)
            else:
                if res is not None:
                    message_type = str_if_bytes(res[0])
                    if message_type == 'unsubscribe':
                        break
                    elif message_type != 'subscribe':
                        await ws_current.send_json(
                            json.loads(str_if_bytes(res[2]))
                        )
        await p.unsubscribe('channel:1')
    await pubsub.close()

async def index(request):
    ws_current = web.WebSocketResponse()

    await ws_current.prepare(request)

    name = request.match_info['username']
    logger.info('%s joined.', name)

    await ws_current.send_json({'action': 'connect', 'name': name})

    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'join', 'name': name})
    request.app['websockets'][name] = ws_current

    redis = get_redis("redis://redis_server")

    await asyncio.gather(
        subscribe(ws_current, redis),
        get_msg(ws_current, request, redis, {'action': 'sent', 'name': name}),
    )

    del request.app['websockets'][name]
    logger.info('%s disconnected.', name)
    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'disconnect', 'name': name})

    return ws_current
