import gc
import os
import time
from random import choice

from models import Journal, engine
from sqlmodel import Session

LEVEL_CHOICE = [10, 20, 30, 40, 50]
count = int(os.environ.get("ITERATIONS", "1000"))

# Objects are created before the timer: the benchmark measures persisting them, not creating them
objs = [Journal(level=choice(LEVEL_CHOICE), text=f"Insert from C, item {i}") for i in range(count)]

# Settle the GC: collect leftovers, keep existing objects out of collections while timed

gc.collect()

gc.freeze()

start = time.time()
with Session(engine) as session:
    session.add_all(objs)
    session.commit()
now = time.time()

print(f"SQLModel, C: Rows/sec: {count / (now - start): 10.2f}")
