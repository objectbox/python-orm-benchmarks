import os
import time
from random import randrange

from models import ORM_NAME, Journal, box, find

LEVEL_CHOICE = [10, 20, 30, 40, 50]
iters = int(os.environ.get("ITERATIONS", "1000"))
start = time.time()

query = box.query(Journal.level.equals(LEVEL_CHOICE[0])).build()
query.limit(20)  # offset()/limit() must not be chained in the beta: they don't return the query

count = 0
for _ in range(iters // 10):
    for level in LEVEL_CHOICE:
        query.set_parameter_int(Journal.level, level)
        query.offset(randrange(iters - 20))
        res = find(query)
        count += len(res)

now = time.time()

print(f"{ORM_NAME}, E: Rows/sec: {count / (now - start): 10.2f}")
