import os
import time
from random import choice

from models import ORM_NAME, new_journal, put, store

LEVEL_CHOICE = [10, 20, 30, 40, 50]
count = int(os.environ.get("ITERATIONS", "1000"))


start = now = time.time()
with store.write_tx():
    for i in range(count):
        put(new_journal(level=choice(LEVEL_CHOICE), text=f"Insert from B, item {i}"))
now = time.time()

print(f"{ORM_NAME}, B: Rows/sec: {count / (now - start): 10.2f}")
