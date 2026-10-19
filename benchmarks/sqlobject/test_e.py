import gc
import os
import time
from random import randrange

from models import Journal

LEVEL_CHOICE = [10, 20, 30, 40, 50]
iters = int(os.environ.get("ITERATIONS", "1000"))

# Settle the GC: collect leftovers, keep existing objects out of collections while timed

gc.collect()

gc.freeze()

start = time.time()
count = 0

for _ in range(iters // 10):
    for level in LEVEL_CHOICE:
        offset = randrange(iters - 20)
        res = list(Journal.select(Journal.q.level == level)[offset : offset + 20])
        count += len(res)

now = time.time()

print(f"SQLObject, E: Rows/sec: {count / (now - start): 10.2f}")
