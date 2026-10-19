import gc
import os
import time

from models import Journal, engine
from sqlalchemy.orm import sessionmaker

LEVEL_CHOICE = [10, 20, 30, 40, 50]
count = int(os.environ.get("ITERATIONS", "1000"))


Session = sessionmaker(bind=engine)

# Settle the GC: collect leftovers, keep existing objects out of collections while timed

gc.collect()

gc.freeze()

start = time.time()
session = Session()
count = 0

for _ in range(10):
    for level in LEVEL_CHOICE:
        res = list(session.query(Journal).filter(Journal.level == level))
        count += len(res)

now = time.time()

print(f"SA ORM, D: Rows/sec: {count / (now - start): 10.2f}")
