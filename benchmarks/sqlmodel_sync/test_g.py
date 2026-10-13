import gc
import time

from models import Journal, engine
from sqlmodel import Session, select

LEVEL_CHOICE = [10, 20, 30, 40, 50]

# Settle the GC: collect leftovers, keep existing objects out of collections while timed

gc.collect()

gc.freeze()

start = time.time()
count = 0
with Session(engine) as session:
    for _ in range(10):
        for level in LEVEL_CHOICE:
            res = [
                value.model_dump()
                for value in session.exec(select(Journal).where(Journal.level == level)).all()
            ]
            count += len(res)
now = time.time()

print(f"SQLModel, G: Rows/sec: {count / (now - start): 10.2f}")
