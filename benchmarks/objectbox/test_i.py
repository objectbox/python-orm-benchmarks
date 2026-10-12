import time
from random import choice

from models import ORM_NAME, get_all, put, store

LEVEL_CHOICE = [10, 20, 30, 40, 50]


objs = get_all()
count = len(objs)

start = time.time()

with store.write_tx():
    for obj in objs:
        obj.level = choice(LEVEL_CHOICE)
        obj.text = f"{obj.text} Update"
        put(obj)

now = time.time()

print(f"{ORM_NAME}, I: Rows/sec: {count / (now - start): 10.2f}")
