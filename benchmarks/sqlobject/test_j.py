import gc
import time
from random import choice

from models import Journal, conn

LEVEL_CHOICE = [10, 20, 30, 40, 50]

trans = conn.transaction()
objs = list(Journal.select(connection=trans))
count = len(objs)
# New values are chosen before the timer: the benchmark measures persisting them
levels = [choice(LEVEL_CHOICE) for _ in objs]

# Settle the GC: collect leftovers, keep existing objects out of collections while timed

gc.collect()

gc.freeze()

start = time.time()

for obj, level in zip(objs, levels):
    obj.level = level
trans.commit(close=True)

now = time.time()

print(f"SQLObject, J: Rows/sec: {count / (now - start): 10.2f}")
