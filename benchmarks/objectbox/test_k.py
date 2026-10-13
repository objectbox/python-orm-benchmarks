import gc
import time

from models import ORM_NAME, box, get_all, store

objs = get_all()
count = len(objs)

# Settle the GC: collect leftovers, keep existing objects out of collections while timed

gc.collect()

gc.freeze()

start = time.time()

with store.write_tx():
    for obj in objs:
        box.remove(obj)

now = time.time()

print(f"{ORM_NAME}, K: Rows/sec: {count / (now - start): 10.2f}")
