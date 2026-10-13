import asyncio
import gc
import os
import time
from random import randint

from models import Journal, SessionLocal

concurrents = int(os.environ.get("CONCURRENTS", "10"))
count = int(os.environ.get("ITERATIONS", "1000"))
maxval = count - 1
count *= 2


async def _runtest(count):
    async with SessionLocal() as session:
        for _ in range(count):
            await session.get(Journal, randint(1, maxval))


async def runtest(loopstr):
    # Settle the GC: collect leftovers, keep existing objects out of collections while timed
    gc.collect()
    gc.freeze()
    start = time.time()
    await asyncio.gather(*[_runtest(count // concurrents) for _ in range(concurrents)])
    now = time.time()
    print(f"SQLModel async{loopstr}, F: Rows/sec: {count / (now - start): 10.2f}")
