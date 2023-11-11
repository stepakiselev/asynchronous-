import asyncio


async def run_five_seconds_timer(secs):
    for secs_left in range(secs, 0, -1):
        print(f'Осталось {secs_left} секунд')
        # print("\a")
        await asyncio.sleep(1)
    print('Время вышло!')
    print('\a')

async def run_thirty_seconds_timer(secs):
    for secs_left in range(secs, 5, -5):
        print(f"осталось {secs_left}")
        await asyncio.sleep(5)

async def run_timer(secs):
    await run_thirty_seconds_timer(secs)
    await run_five_seconds_timer(5)

loop = asyncio.get_event_loop()

loop.create_task(run_five_seconds_timer(5))

loop.run_forever()

# coroutine = run_timer(3)
# asyncio.run(coroutine)

#coroutine2 = run_timer(30)
# asyncio.run(coroutine2)
