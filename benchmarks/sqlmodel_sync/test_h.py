import time

from models import Journal, engine
from sqlalchemy import select
from sqlmodel import Session

LEVEL_CHOICE = [10, 20, 30, 40, 50]

start = time.time()
count = 0
with Session(engine) as session:
    for _ in range(10):
        for level in LEVEL_CHOICE:
            res = session.execute(
                select(*Journal.__table__._columns).where(Journal.__table__.c.level == level)
            ).all()
            count += len(res)
now = time.time()

print(f"SQLModel, H: Rows/sec: {count / (now - start): 10.2f}")
