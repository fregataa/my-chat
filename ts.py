import asyncio

async def aprint(s):
    print(s)
    await asyncio.sleep(0)

async def count_down(n):
    for i in range(n, 0, -1):
        await aprint(f"Counting down: {i}")
        # await asyncio.sleep(0)

async def count_up(n):
    for i in range(1, n+1):
        await aprint(f"Counting up: {i}")
        # await asyncio.sleep(0)

async def main():
    await asyncio.gather(count_down(5), count_up(5))

if __name__ == "__main__":
    asyncio.run(main())