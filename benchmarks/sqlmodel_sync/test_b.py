import os
import time
from random import choice

from models import Journal, engine
from sqlmodel import Session

LEVEL_CHOICE = [10, 20, 30, 40, 50]
count = int(os.environ.get("ITERATIONS", "1000"))

start = time.time()
with Session(engine) as session:
    for i in range(count):
        session.add(Journal(level=choice(LEVEL_CHOICE), text=f"Insert from B, item {i}"))
    session.commit()
now = time.time()

print(f"SQLModel, B: Rows/sec: {count / (now - start): 10.2f}")
