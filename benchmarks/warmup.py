#!/usr/bin/env python
"""Warm-up mode (WARMUP=1, SQLite only): run each operation once untimed, restore the DB, time it.

The warm-up run sees the same DB state as the measured run, so the measured run starts in a process
(or event loop) that has already done the same work: imports, connections, compiled statements and
caches, ObjectBox's codegen. Before the measured run the DB is restored to the state before the
warm-up run (rows, ID sequences), so both runs do the same work. Output is the usual Rows/sec line.

Sync ORMs: bench.sh runs `python ../warmup.py <module>` instead of `python -m <module>`.
Async ORMs: bench.py calls `await warm(test_x.runtest, loopstr)` for each test.
"""

import contextlib
import gc
import os
import runpy
import shutil
import sqlite3
import sys

SQLITE_DB = "/tmp/db.sqlite3"
OBJECTBOX_DIR = "/tmp/objectbox-bench"


def enabled():
    if os.environ.get("WARMUP", "0") in ("", "0"):
        return False
    if os.environ.get("DBTYPE", "sqlite") not in ("", "sqlite"):
        sys.exit("WARMUP=1 is only implemented for DBTYPE=sqlite")
    return True


class Snapshot:
    """Copy of the DB state, restored after the warm-up run."""

    def __init__(self):
        self.objectbox = os.path.basename(os.getcwd()) == "objectbox"
        if self.objectbox:
            # The sync runner takes it before the test imports models, so the store is closed
            self.files = {}
            for name in os.listdir(OBJECTBOX_DIR):
                with open(os.path.join(OBJECTBOX_DIR, name), "rb") as f:
                    self.files[name] = f.read()
        else:
            # The backup API copies a consistent state while the ORM's connections stay open,
            # including sqlite_sequence (AUTOINCREMENT counters).
            self.mem = sqlite3.connect(":memory:")
            with contextlib.closing(sqlite3.connect(SQLITE_DB)) as db:
                db.backup(self.mem)

    def restore(self):
        if self.objectbox:
            models = sys.modules["models"]

            def write_back():
                # Synced, so the measured run's first commit doesn't also flush these pages
                shutil.rmtree(OBJECTBOX_DIR)
                os.mkdir(OBJECTBOX_DIR)
                for name, data in self.files.items():
                    with open(os.path.join(OBJECTBOX_DIR, name), "wb") as f:
                        f.write(data)
                        os.fsync(f.fileno())
                dir_fd = os.open(OBJECTBOX_DIR, os.O_RDONLY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)

            models.reopen(write_back)
        else:
            with contextlib.closing(sqlite3.connect(SQLITE_DB)) as db:
                self.mem.backup(db)
                if db.execute("PRAGMA journal_mode").fetchone()[0] == "wal":  # peewee, Tortoise ORM
                    # The restored pages are in the WAL: write them to the DB file now, so the
                    # measured run's commit doesn't run the auto-checkpoint that does it
                    busy, _, _ = db.execute("PRAGMA wal_checkpoint(RESTART)").fetchone()
                    if busy:
                        sys.exit("warmup: WAL checkpoint after the restore was blocked")
                    # Start the new WAL with a no-op write: with synchronous=FULL, the first commit
                    # to a restarted WAL also syncs its header. The measured run's commit appends,
                    # as in a cold run, where the WAL still holds the previous process's frames
                    version = db.execute("PRAGMA user_version").fetchone()[0]
                    db.execute(f"PRAGMA user_version = {version}")
            self.mem.close()
        clear_orm_caches()
        gc.collect()


def db_state():
    """Row count and highest ID per table, for WARMUP_CHECK=1."""
    if os.path.basename(os.getcwd()) == "objectbox":
        ids = [obj.id for obj in sys.modules["models"].box.get_all()]
        return {"Journal": (len(ids), max(ids, default=0))}
    with contextlib.closing(sqlite3.connect(SQLITE_DB)) as db:
        tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
        return {t: db.execute(f'SELECT count(*), max(rowid) FROM "{t}"').fetchone() for t in tables}


def check(name, warmup_state):
    """WARMUP_CHECK=1: the measured run must leave the same row counts and IDs as the warm-up."""
    state = db_state()
    status = "ok" if state == warmup_state else f"MISMATCH: {warmup_state} vs. {state}"
    print(f"warmup check {name}: {status}", file=sys.stderr)


def clear_orm_caches():
    """Drops row caches that would let the measured run skip reading rows seen in the warm-up."""
    sqlobject = sys.modules.get("sqlobject")
    if sqlobject is not None and sqlobject.sqlhub.processConnection is not None:
        sqlobject.sqlhub.processConnection.cache.clear()


async def warm(runtest, loopstr):
    """Async ORMs: warm-up run (output discarded), restore, measured run."""
    if enabled():
        snapshot = Snapshot()
        with contextlib.redirect_stdout(open(os.devnull, "w")):
            await runtest(loopstr)
        checking = os.environ.get("WARMUP_CHECK") == "1"
        warmup_state = db_state() if checking else None
        snapshot.restore()
    await runtest(loopstr)
    if enabled() and checking:
        check(runtest.__module__, warmup_state)


def main():
    module = sys.argv[1]
    sys.path[0] = os.getcwd()  # like `python -m <module>` run from the ORM directory
    if enabled():
        snapshot = Snapshot()
        with contextlib.redirect_stdout(open(os.devnull, "w")):
            runpy.run_module(module, run_name="__main__", alter_sys=False)
        checking = os.environ.get("WARMUP_CHECK") == "1"
        warmup_state = db_state() if checking else None
        snapshot.restore()
    runpy.run_module(module, run_name="__main__", alter_sys=False)
    if enabled() and checking:
        check(module, warmup_state)


if __name__ == "__main__":
    main()
