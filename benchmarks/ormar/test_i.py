import asyncio
import gc
import os
import time
from random import choice

from models import Journal, database

LEVEL_CHOICE = [10, 20, 30, 40, 50]
concurrents = int(os.environ.get("CONCURRENTS", "10"))


async def _runtest(objs, values) -> int:
    async with database.transaction():
        for obj, (level, text) in zip(objs, values):
            obj.level = level
            obj.text = text
            await obj.update()
    return len(objs)


async def runtest(loopstr):
    objs = await Journal.objects.all()
    inrange = len(objs) // concurrents
    if inrange < 1:
        inrange = 1

    # New values are chosen before the timer: the benchmark measures persisting them
    values = [(choice(LEVEL_CHOICE), f"{obj.text} Update") for obj in objs]
    # Settle the GC: collect leftovers, keep existing objects out of collections while timed
    gc.collect()
    gc.freeze()
    start = time.time()
    count = sum(
        await asyncio.gather(
            *[
                _runtest(
                    objs[i * inrange : (i + 1) * inrange], values[i * inrange : (i + 1) * inrange]
                )
                for i in range(concurrents)
            ]
        )
    )
    now = time.time()
    print(f"ormar{loopstr}, I: Rows/sec: {count / (now - start): 10.2f}")
