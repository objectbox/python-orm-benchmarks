import os
import time
from random import randint

from models import Journal, engine
from sqlmodel import Session

count = int(os.environ.get("ITERATIONS", "1000"))
maxval = count - 1
count *= 2

start = time.time()
with Session(engine) as session:
    for _ in range(count):
        session.get(Journal, randint(1, maxval))
now = time.time()

print(f"SQLModel, F: Rows/sec: {count / (now - start): 10.2f}")
