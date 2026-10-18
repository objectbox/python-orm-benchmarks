import asyncio
import gc
import os
import time
from random import choice

from models import Journal, database

LEVEL_CHOICE = [10, 20, 30, 40, 50]
concurrents = int(os.environ.get("CONCURRENTS", "10"))
count = int(os.environ.get("BATCH_SIZE", "10000"))
count = int(count // concurrents) * concurrents


# SQLite allows at most 32,766 variables per statement (Test 3: ~36 columns): insert in chunks
CHUNK_SIZE = 32766 // len(Journal.ormar_config.table.columns)


async def _runtest(objs):
    async with database.transaction():
        for i in range(0, len(objs), CHUNK_SIZE):
            await Journal.objects.bulk_create(objs[i : i + CHUNK_SIZE])


async def runtest(loopstr):
    # Objects are created before the timer: the benchmark measures persisting, not creating them
    batches = [
        [
            Journal(level=choice(LEVEL_CHOICE), text=f"Insert from C, item {i}")
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
    print(f"ormar{loopstr}, C: Rows/sec: {count / (now - start): 10.2f}")
