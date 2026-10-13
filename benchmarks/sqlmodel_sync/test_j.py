import gc
import time
from random import choice

from models import Journal, engine
from sqlmodel import Session, select

LEVEL_CHOICE = [10, 20, 30, 40, 50]

with Session(engine) as session:
    objs = session.exec(select(Journal)).all()
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

print(f"SQLModel, J: Rows/sec: {count / (now - start): 10.2f}")
