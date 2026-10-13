import gc
import os
import time
from random import choice

from models import Journal, conn

LEVEL_CHOICE = [10, 20, 30, 40, 50]

count = int(os.environ.get("ITERATIONS", "1000"))
# SQLObject inserts the row when creating the object: only the values are prepared before the timer
values = [dict(level=choice(LEVEL_CHOICE), text=f"Insert from B, item {i}") for i in range(count)]

# Settle the GC: collect leftovers, keep existing objects out of collections while timed

gc.collect()

gc.freeze()

start = now = time.time()
trans = conn.transaction()
for kwargs in values:
    Journal(**kwargs, connection=trans)
trans.commit(close=True)
now = time.time()

print(f"SQLObject, B: Rows/sec: {count / (now - start): 10.2f}")
