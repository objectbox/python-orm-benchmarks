"""Untimed, after B and C: remove the newest BATCH_SIZE - ITERATIONS objects again (see ../trim.py)."""

import os

from models import Journal, box, store

if os.environ.get("LARGE_TABLE", "0") == "0":
    extra = int(os.environ.get("BATCH_SIZE", "10000")) - int(os.environ.get("ITERATIONS", "1000"))
    ids = sorted(box.query(Journal.id.greater_than(0)).build().find_ids())
    if extra > 0 and len(ids) > extra:
        with store.write_tx():
            box.query(Journal.id.greater_than(ids[-extra - 1])).build().remove()
