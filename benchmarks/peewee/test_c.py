import gc
import os
import time
from random import choice

from models import Journal, db

LEVEL_CHOICE = [10, 20, 30, 40, 50]
CHUNK_SIZE = 100
count = int(os.environ.get("BATCH_SIZE", "10000"))

# Work around peewee bulk-insert limitation that is total of 2000 values
test = int(os.environ.get("TEST", "1"))
if test == 3:
    CHUNK_SIZE = 50

chunks = count // CHUNK_SIZE
# Rows are created before the timer: the benchmark measures persisting them, not creating them
rows = [
    [(choice(LEVEL_CHOICE), f"Insert from C, item {i}") for i in range(CHUNK_SIZE)]
    for _ in range(chunks)
]

# Settle the GC: collect leftovers, keep existing objects out of collections while timed

gc.collect()

gc.freeze()

start = now = time.time()
with db.atomic():
    for chunk in rows:
        Journal.insert_many(chunk, [Journal.level, Journal.text]).execute()
now = time.time()

print(f"peewee, C: Rows/sec: {count / (now - start): 10.2f}")
