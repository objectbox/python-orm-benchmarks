import asyncio
import gc
import os
import time
from random import randrange

from models import Journal, SessionLocal
from sqlmodel import select

LEVEL_CHOICE = [10, 20, 30, 40, 50]
iters = int(os.environ.get("ITERATIONS", "1000"))
concurrents = int(os.environ.get("CONCURRENTS", "10"))


async def _runtest(_iters) -> int:
    count = 0
    async with SessionLocal() as session:
        for _ in range(_iters):
            for level in LEVEL_CHOICE:
                result = await session.exec(
                    select(Journal).where(Journal.level == level).limit(20).offset(randrange(iters - 20))
                )
                res = result.all()
                count += len(res)
    return count


async def runtest(loopstr):
    # Settle the GC: collect leftovers, keep existing objects out of collections while timed
    gc.collect()
    gc.freeze()
    start = time.time()
    count = sum(
        await asyncio.gather(*[_runtest(iters // 10 // concurrents) for _ in range(concurrents)])
    )
    now = time.time()
    print(f"SQLModel async{loopstr}, E: Rows/sec: {count / (now - start): 10.2f}")
