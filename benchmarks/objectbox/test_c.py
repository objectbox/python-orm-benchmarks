import gc
import os
import time
from random import choice

from models import ORM_NAME, new_journal, put

LEVEL_CHOICE = [10, 20, 30, 40, 50]
count = int(os.environ.get("BATCH_SIZE", "10000"))


# Objects are created before the timer: the benchmark measures persisting them, not creating them
objs = [
    new_journal(level=choice(LEVEL_CHOICE), text=f"Insert from C, item {i}") for i in range(count)
]

# Settle the GC: collect leftovers, keep existing objects out of collections while timed

gc.collect()

gc.freeze()

start = now = time.time()
put(objs)
now = time.time()

print(f"{ORM_NAME}, C: Rows/sec: {count / (now - start): 10.2f}")
