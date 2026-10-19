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
    values = [(choice(LEVEL_CHOICE), f"{obj.text} Update") for obj in objs]

    # Settle the GC: collect leftovers, keep existing objects out of collections while timed

    gc.collect()

    gc.freeze()

    start = time.time()
    for obj, (level, text) in zip(objs, values):
        obj.level = level
        obj.text = text
        session.add(obj)
    session.commit()
    now = time.time()

print(f"SQLModel, I: Rows/sec: {count / (now - start): 10.2f}")
