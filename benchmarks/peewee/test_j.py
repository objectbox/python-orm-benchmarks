import gc
import time
from random import choice

from models import Journal, db

LEVEL_CHOICE = [10, 20, 30, 40, 50]


objs = list(Journal.select())
count = len(objs)

# New values are chosen before the timer: the benchmark measures persisting them
levels = [choice(LEVEL_CHOICE) for _ in objs]

# Settle the GC: collect leftovers, keep existing objects out of collections while timed

gc.collect()

gc.freeze()

start = time.time()

with db.atomic():
    for obj, level in zip(objs, levels):
        obj.level = level
        obj.save(only=["level"])

now = time.time()

print(f"peewee, J: Rows/sec: {count / (now - start): 10.2f}")
