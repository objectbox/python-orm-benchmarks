import gc
import os
import time
from random import randrange

from models import Journal, engine
from sqlmodel import Session, select

LEVEL_CHOICE = [10, 20, 30, 40, 50]
iters = int(os.environ.get("ITERATIONS", "1000"))

# Settle the GC: collect leftovers, keep existing objects out of collections while timed

gc.collect()

gc.freeze()

start = time.time()
count = 0
with Session(engine) as session:
    for _ in range(iters // 10):
        for level in LEVEL_CHOICE:
            res = session.exec(
                select(Journal)
                .where(Journal.level == level)
                .limit(20)
                .offset(randrange(iters - 20))
            ).all()
            count += len(res)
now = time.time()

print(f"SQLModel, E: Rows/sec: {count / (now - start): 10.2f}")
