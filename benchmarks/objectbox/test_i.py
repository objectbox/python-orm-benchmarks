import gc
import time
from random import choice

from models import ORM_NAME, get_all, put, store

LEVEL_CHOICE = [10, 20, 30, 40, 50]


objs = get_all()
count = len(objs)

# New values are chosen before the timer: the benchmark measures persisting them
values = [(choice(LEVEL_CHOICE), f"{obj.text} Update") for obj in objs]

# Settle the GC: collect leftovers, keep existing objects out of collections while timed

gc.collect()

gc.freeze()

start = time.time()

with store.write_tx():
    for obj, (level, text) in zip(objs, values):
        obj.level = level
        obj.text = text
        put(obj)

now = time.time()

print(f"{ORM_NAME}, I: Rows/sec: {count / (now - start): 10.2f}")
