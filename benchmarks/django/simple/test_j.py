try:
    import django  # noqa

    django.setup()  # noqa
finally:
    pass

import gc
import time
from random import choice

from django.db import transaction
from simple.models import Journal

LEVEL_CHOICE = [10, 20, 30, 40, 50]


objs = list(Journal.objects.all())
count = len(objs)

# New values are chosen before the timer: the benchmark measures persisting them
levels = [choice(LEVEL_CHOICE) for _ in objs]

# Settle the GC: collect leftovers, keep existing objects out of collections while timed

gc.collect()

gc.freeze()

start = time.time()

with transaction.atomic():
    for obj, level in zip(objs, levels):
        obj.level = level
        obj.save(update_fields=["level"])

now = time.time()

print(f"Django, J: Rows/sec: {count / (now - start): 10.2f}")
