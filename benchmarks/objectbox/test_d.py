import time

from models import ORM_NAME, Journal, box, find

LEVEL_CHOICE = [10, 20, 30, 40, 50]
start = time.time()

# The query is built once and re-run with a new parameter, the idiomatic ObjectBox way
query = box.query(Journal.level.equals(LEVEL_CHOICE[0])).build()

count = 0
for _ in range(10):
    for level in LEVEL_CHOICE:
        query.set_parameter_int(Journal.level, level)
        res = find(query)
        count += len(res)

now = time.time()

print(f"{ORM_NAME}, D: Rows/sec: {count / (now - start): 10.2f}")
