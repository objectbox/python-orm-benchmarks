import time
from random import choice

from models import ORM_NAME, get_all, put, store

LEVEL_CHOICE = [10, 20, 30, 40, 50]


objs = get_all()
count = len(objs)

start = time.time()

# No partial updates in ObjectBox: put() always writes the whole object
with store.write_tx():
    for obj in objs:
        obj.level = choice(LEVEL_CHOICE)
        put(obj)

now = time.time()

print(f"{ORM_NAME}, J: Rows/sec: {count / (now - start): 10.2f}")
