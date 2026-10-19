import asyncio
import gc
import os
import time
from random import choice

from models import Journal, SessionLocal
from sqlalchemy import select

LEVEL_CHOICE = [10, 20, 30, 40, 50]
concurrents = int(os.environ.get("CONCURRENTS", "10"))


async def _runtest(objs, values) -> int:
    async with SessionLocal() as session:
        for obj, (level, text) in zip(objs, values):
            # load=False: the objects were loaded before, so no SELECT per object
            merged = await session.merge(obj, load=False)
            merged.level = level
            merged.text = text
        await session.commit()
    return len(objs)


async def runtest(loopstr):
    async with SessionLocal() as session:
        result = await session.execute(select(Journal))
        objs = result.scalars().all()

    count_obj = len(objs)
    inrange = count_obj // concurrents
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
                    objs[i * inrange : ((i + 1) * inrange)],
                    values[i * inrange : ((i + 1) * inrange)],
                )
                for i in range(concurrents)
            ]
        )
    )
    now = time.time()
    print(f"SA ORM async{loopstr}, I: Rows/sec: {count / (now - start): 10.2f}")
