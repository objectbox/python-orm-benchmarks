import asyncio
import gc
import os
import time
from random import choice

from models import DB, Journal

LEVEL_CHOICE = [10, 20, 30, 40, 50]
concurrents = int(os.environ.get("CONCURRENTS", "10"))


async def _runtest(objs, levels) -> int:
    async with DB.transaction():
        for obj, level in zip(objs, levels):
            obj.level = level
            await obj.save()
    return len(objs)


async def runtest(loopstr):
    objs = await Journal.objects()
    inrange = len(objs) // concurrents
    if inrange < 1:
        inrange = 1

    # New values are chosen before the timer: the benchmark measures persisting them
    levels = [choice(LEVEL_CHOICE) for _ in objs]
    # Settle the GC: collect leftovers, keep existing objects out of collections while timed
    gc.collect()
    gc.freeze()
    start = time.time()
    count = sum(
        await asyncio.gather(
            *[
                _runtest(
                    objs[i * inrange : (i + 1) * inrange], levels[i * inrange : (i + 1) * inrange]
                )
                for i in range(concurrents)
            ]
        )
    )
    now = time.time()
    print(f"Piccolo{loopstr}, J: Rows/sec: {count / (now - start): 10.2f}")
