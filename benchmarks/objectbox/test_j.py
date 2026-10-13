import gc
import time
from random import choice

from models import ORM_NAME, get_all, put, store

LEVEL_CHOICE = [10, 20, 30, 40, 50]


objs = get_all()
count = len(objs)

# New values are chosen before the timer: the benchmark measures persisting them
levels = [choice(LEVEL_CHOICE) for _ in objs]

# Settle the GC: collect leftovers, keep existing objects out of collections while timed

gc.collect()

gc.freeze()

start = time.time()

# No partial updates in ObjectBox: put() always writes the whole object
with store.write_tx():
    for obj, level in zip(objs, levels):
        obj.level = level
        put(obj)

now = time.time()

print(f"{ORM_NAME}, J: Rows/sec: {count / (now - start): 10.2f}")
