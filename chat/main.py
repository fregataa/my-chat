import asyncio

from aiohttp import web
import aioredis
from aiohttp_session import setup
from aiohttp_session.redis_storage import RedisStorage

from routes import setup_routes

async def start_server():
    app = web.Application()

    redis = await aioredis.from_url('redis://localhost')
    storage = RedisStorage(redis)
    setup(app, storage)

    setup_routes(app)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner,
        '0.0.0.0',
        '8080',
        reuse_port=True,
    )
    await site.start()

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.ensure_future(start_server())
    loop.run_forever()

if __name__ == '__main__':
    main()