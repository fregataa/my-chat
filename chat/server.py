import asyncio
import logging

from aiohttp import web
import aioredis
from aiohttp_session import setup
from aiohttp_session.redis_storage import RedisStorage

from views import index

logger = logging.getLogger('mychat.server')
logging.basicConfig(level=logging.INFO)

async def start_server():
    app = web.Application()

    redis_url = 'redis://localhost'
    redis = await aioredis.from_url(redis_url)
    storage = RedisStorage(redis)
    app['websockets'] = {}

    # app.on_shutdown.append(shutdown)

    # aiohttp_jinja2.setup(
    #     app, loader=jinja2.PackageLoader('chat', 'templates'))

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
    loop.create_task(start_server())
    loop.run_forever()

if __name__ == '__main__':
    main()
