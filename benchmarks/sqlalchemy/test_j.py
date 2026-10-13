import gc
import os
import time
from random import choice

from models import Journal, engine
from sqlalchemy.orm import sessionmaker

LEVEL_CHOICE = [10, 20, 30, 40, 50]
count = int(os.environ.get("ITERATIONS", "1000"))


Session = sessionmaker(bind=engine)
session = Session()

objs = list(session.query(Journal).all())
count = len(objs)

# New values are chosen before the timer: the benchmark measures persisting them
levels = [choice(LEVEL_CHOICE) for _ in objs]

# Settle the GC: collect leftovers, keep existing objects out of collections while timed

gc.collect()

gc.freeze()

start = time.time()

for obj, level in zip(objs, levels):
    obj.level = level
    session.add(obj)
session.commit()

now = time.time()

print(f"SA ORM, J: Rows/sec: {count / (now - start): 10.2f}")
