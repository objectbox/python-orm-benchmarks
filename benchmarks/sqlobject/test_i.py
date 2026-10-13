import gc
import time
from random import choice

from models import Journal, conn

LEVEL_CHOICE = [10, 20, 30, 40, 50]

trans = conn.transaction()
objs = list(Journal.select(connection=trans))
count = len(objs)
# New values are chosen before the timer: the benchmark measures persisting them
values = [(choice(LEVEL_CHOICE), f"{obj.text} Update") for obj in objs]

# Settle the GC: collect leftovers, keep existing objects out of collections while timed

gc.collect()

gc.freeze()

start = time.time()

for obj, (level, text) in zip(objs, values):
    obj.level = level
    obj.text = text
trans.commit(close=True)

now = time.time()

print(f"SQLObject, I: Rows/sec: {count / (now - start): 10.2f}")
