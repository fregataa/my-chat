
import logging

from aiohttp import web, WSMsgType
import aioredis

logger = logging.getLogger('mychat.server')
logging.basicConfig(level=logging.INFO)

class InvalidCommand(web.HTTPBadRequest):
    reason = 'Invalid type of command'

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
                if ws is ws_current:
                    match msg.data.split()[0]:
                        case 'set:':
                            set_prefix = 'set: '
                            input_data = msg.data[len(set_prefix):].split(',')
                            if len(input_data) != 2:
                                raise InvalidCommand
                            redis = aioredis.from_url(
                                "redis://redis_server", encoding="utf-8", decode_responses=True
                            )
                            await redis.set(input_data[0], input_data[1])
                            log_msg = f'Completed set command. key: {input_data[0]}, val: {input_data[1]}'
                            logger.info(log_msg)
                        case 'get:':
                            get_prefix = 'get: '
                            input_data = msg.data[len(get_prefix):].split()
                            if len(input_data) != 1:
                                raise InvalidCommand
                            redis = aioredis.from_url(
                                "redis://redis_server", encoding="utf-8", decode_responses=True
                            )
                            val = await redis.get(input_data[0])
                            await ws.send_json(
                                {'action': 'get', 'key': input_data[0], 'val': val}
                            )
                            log_msg = f'Completed get command. key: {input_data[0]}, val: {val}'
                            logger.info(log_msg)
                        case _:
                            pass

                else:
                    await ws.send_json(
                        {'action': 'sent', 'name': name, 'text': msg.data})
        else:
            break

    del request.app['websockets'][name]
    logger.info('%s disconnected.', name)
    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'disconnect', 'name': name})

    return ws_current
