import os
import time
from random import choice

from models import ORM_NAME, new_journal, put

LEVEL_CHOICE = [10, 20, 30, 40, 50]
count = int(os.environ.get("ITERATIONS", "1000"))


start = now = time.time()
put(
    [new_journal(level=choice(LEVEL_CHOICE), text=f"Insert from C, item {i}") for i in range(count)]
)
now = time.time()

print(f"{ORM_NAME}, C: Rows/sec: {count / (now - start): 10.2f}")
