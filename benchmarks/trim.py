#!/usr/bin/env python
"""Untimed, after B and C: shrink the table back to the size D-K were designed for.

B and C insert BATCH_SIZE rows (default 10000) so their transactions measure insert throughput,
not mostly one durable commit. D-K run on the whole table, so this deletes the newest
BATCH_SIZE - ITERATIONS rows again: each of B and C leaves ITERATIONS rows, as before.
LARGE_TABLE=1 keeps all rows (D-K then run on ~2 x BATCH_SIZE rows). SQLite only; with
PostgreSQL/MySQL the rows stay. ObjectBox has its own objectbox/trim.py.
"""

import os
import sqlite3
import sys


def trim(table="journal"):
    if os.environ.get("LARGE_TABLE", "0") != "0" or os.environ.get("DBTYPE", "sqlite") != "sqlite":
        return
    extra = int(os.environ.get("BATCH_SIZE", "10000")) - int(os.environ.get("ITERATIONS", "1000"))
    if extra <= 0:
        return
    conn = sqlite3.connect("/tmp/db.sqlite3", timeout=60)
    try:
        with conn:
            conn.execute(
                f'DELETE FROM "{table}" WHERE rowid IN '
                f'(SELECT rowid FROM "{table}" ORDER BY rowid DESC LIMIT ?)',
                (extra,),
            )
    finally:
        conn.close()


if __name__ == "__main__":
    trim(*sys.argv[1:])  # Django: simple_journal<TEST>
