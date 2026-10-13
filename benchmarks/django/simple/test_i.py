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
values = [(choice(LEVEL_CHOICE), f"{obj.text} Update") for obj in objs]

# Settle the GC: collect leftovers, keep existing objects out of collections while timed

gc.collect()

gc.freeze()

start = time.time()

with transaction.atomic():
    for obj, (level, text) in zip(objs, values):
        obj.level = level
        obj.text = text
        obj.save()

now = time.time()

print(f"Django, I: Rows/sec: {count / (now - start): 10.2f}")
