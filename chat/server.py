import asyncio
import logging

from aiohttp import web
import aioredis
from aiohttp_session import setup
from aiohttp_session.redis_storage import RedisStorage

from views import index

logger = logging.getLogger('mychat.server')
logging.basicConfig(level=logging.INFO)

def cancel_tasks(to_cancel, loop):
    if not to_cancel:
        return
    
    for task in to_cancel:
        task.cancel()
    
    loop.run_until_complete(asyncio.gather(*to_cancel, return_exceptions=True))
    
    for task in to_cancel:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler(
                {
                    'message': 'Unhandled exception during asyncio.run() shutdown',
                    'exception': task.exception(),
                    'task': task,
                }
            )

async def shutdown(app):
    for mw in app.middlewares:
        await mw.close()
    for ws in app['websockets'].values():
        await ws.close()
    app['websockets'].clear()

async def start_server():
    app = web.Application()

    redis_url = 'redis://localhost'
    redis = await aioredis.from_url(redis_url)
    storage = RedisStorage(redis)
    app['websockets'] = {}

    app.on_shutdown.append(shutdown)

    setup(app, storage)

    app.router.add_get('/{username}', index)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner,
        '0.0.0.0',
        '8080',
        reuse_port=True,
    )

    logger.info("Start server.")
    await site.start()

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server_task = loop.create_task(start_server())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.exception(e)
    finally:
        cancel_tasks({server_task}, loop)
        cancel_tasks(asyncio.all_tasks(loop), loop)
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        asyncio.set_event_loop(None)

if __name__ == '__main__':
    main()
