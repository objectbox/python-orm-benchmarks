import asyncio
import gc
import os
import time
from random import choice

from models import Journal, database

LEVEL_CHOICE = [10, 20, 30, 40, 50]
concurrents = int(os.environ.get("CONCURRENTS", "10"))
count = int(os.environ.get("ITERATIONS", "1000"))
count = int(count // concurrents) * concurrents


async def _runtest(objs):
    async with database.transaction():
        for obj in objs:
            await obj.save()  # what Journal.objects.create() does after creating the object


async def runtest(loopstr):
    # Objects are created before the timer: the benchmark measures persisting, not creating them
    batches = [
        [
            Journal(level=choice(LEVEL_CHOICE), text=f"Insert from B, item {i}")
            for i in range(count // concurrents)
        ]
        for _ in range(concurrents)
    ]

    # Settle the GC: collect leftovers, keep existing objects out of collections while timed

    gc.collect()

    gc.freeze()

    start = time.time()
    await asyncio.gather(*[_runtest(objs) for objs in batches])
    now = time.time()
    print(f"ormar{loopstr}, B: Rows/sec: {count / (now - start): 10.2f}")
