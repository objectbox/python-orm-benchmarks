import asyncio
import gc
import os
import time

from models import Journal, SessionLocal
from sqlmodel import select

concurrents = int(os.environ.get("CONCURRENTS", "10"))


async def _runtest(objs) -> int:
    async with SessionLocal() as session:
        for obj in objs:
            merged = await session.merge(obj)
            await session.delete(merged)
        await session.commit()
    return len(objs)


async def runtest(loopstr):
    async with SessionLocal() as session:
        result = await session.exec(select(Journal))
        objs = result.all()

    count_obj = len(objs)
    inrange = count_obj // concurrents
    if inrange < 1:
        inrange = 1

    # Settle the GC: collect leftovers, keep existing objects out of collections while timed

    gc.collect()

    gc.freeze()

    start = time.time()
    count = sum(
        await asyncio.gather(
            *[_runtest(objs[i * inrange : ((i + 1) * inrange)]) for i in range(concurrents)]
        )
    )
    now = time.time()
    print(f"SQLModel async{loopstr}, K: Rows/sec: {count / (now - start): 10.2f}")
