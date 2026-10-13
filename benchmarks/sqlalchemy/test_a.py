import gc
import os
import time
from random import choice

from models import Journal, engine
from sqlalchemy.orm import sessionmaker

LEVEL_CHOICE = [10, 20, 30, 40, 50]
count = int(os.environ.get("ITERATIONS", "1000"))


Session = sessionmaker(bind=engine)
# Objects are created before the timer: the benchmark measures persisting them, not creating them
objs = [Journal(level=choice(LEVEL_CHOICE), text=f"Insert from A, item {i}") for i in range(count)]

# Settle the GC: collect leftovers, keep existing objects out of collections while timed

gc.collect()

gc.freeze()

start = now = time.time()
session = Session()
for obj in objs:
    session.add(obj)
    session.commit()
now = time.time()

print(f"SA ORM, A: Rows/sec: {count / (now - start): 10.2f}")
