import gc
import time

from models import Journal, engine
from sqlmodel import Session, select

with Session(engine) as session:
    objs = session.exec(select(Journal)).all()
    count = len(objs)

    # Settle the GC: collect leftovers, keep existing objects out of collections while timed

    gc.collect()

    gc.freeze()

    start = time.time()
    for obj in objs:
        session.delete(obj)
    session.commit()
    now = time.time()

print(f"SQLModel, K: Rows/sec: {count / (now - start): 10.2f}")
