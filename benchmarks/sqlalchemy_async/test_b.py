import asyncio
import gc
import os
import time
from random import choice

from models import Journal, SessionLocal

LEVEL_CHOICE = [10, 20, 30, 40, 50]
concurrents = int(os.environ.get("CONCURRENTS", "10"))
count = int(os.environ.get("BATCH_SIZE", "10000"))
count = int(count // concurrents) * concurrents


async def _runtest(objs):
    async with SessionLocal() as session:
        for obj in objs:
            session.add(obj)
        await session.commit()


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
    print(f"SA ORM async{loopstr}, B: Rows/sec: {count / (now - start): 10.2f}")
