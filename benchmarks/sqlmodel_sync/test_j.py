import time
from random import choice

from models import Journal, engine
from sqlmodel import Session, select

LEVEL_CHOICE = [10, 20, 30, 40, 50]

with Session(engine) as session:
    objs = session.exec(select(Journal)).all()
    count = len(objs)

    start = time.time()
    for obj in objs:
        obj.level = choice(LEVEL_CHOICE)
        session.add(obj)
    session.commit()
    now = time.time()

print(f"SQLModel, J: Rows/sec: {count / (now - start): 10.2f}")
