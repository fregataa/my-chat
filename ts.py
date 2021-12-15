import asyncio
# import time

async def hello():
    while True:
        print("Hello")
        await asyncio.sleep(3)
        print("World!")

async def do_something():
    while True:
        print("Do something ...")
        asyncio.sleep(1)

async def main():
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    t1 = await loop.create_task(hello())
    t2 = await loop.create_task(do_something())

    # asyncio.ensure_future(hello())
    # asyncio.ensure_future(do_something())

    # loop.run_until_complete(t1)
    # loop.run_until_complete(t2)

if __name__=="__main__":
    asyncio.run(main())
