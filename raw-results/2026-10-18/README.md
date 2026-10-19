# Raw results, 2026-10-18

The data behind the SQLite tables and charts in the main README and in `../../large-table.md`. They replace the results of `../2026-10-13/`.

| Directory | Mode | Published as |
|-----------|------|--------------|
| `sqlite/` | cold | README, `images/sqlite_*.png` |
| `sqlite-warm/` | warm (`WARMUP=1`) | README, `images/sqlite_warm_*.png` |
| `sqlite-large/` | cold, large table (`LARGE_TABLE=1`) | README (summary), `large-table.md`, `images/sqlite_large_*.png` |
| `sqlite-large-warm/` | warm, large table (`WARMUP=1 LARGE_TABLE=1`) | README (summary), `large-table.md`, `images/sqlite_large_warm_*.png` |

- `run1` … `run5`: the raw `bench.sh` output of 5 full SQLite runs (all ORMs and ObjectBox, Tests 1–3, `ITERATIONS=100`, `BATCH_SIZE=10000`), one `outfile<test>` per test model. Besides the `Rows/sec` lines they contain the ORMs' warnings (e.g. Django's system check).
- `median/`: the median of the 5 runs for each ORM and operation; the tables and charts are generated from these files.

The modes ran one after the other, from 2026-10-18 22:30 to 2026-10-19 05:00: 5 cold runs, 5 warm, 5 cold large-table, 5 warm large-table runs, all ORMs in each run.

peewee and Tortoise ORM were rerun in both warm modes on 2026-10-19 (5 runs each, same settings) after a fix to the warm-up restore (see below): their runs replace the peewee and Tortoise ORM lines in each `run<n>/outfile<test>` of `sqlite-warm/` and `sqlite-large-warm/` and are appended at the end. The replaced lines are kept in `superseded/warmup-wal/`.

## Changes since 2026-10-13

- B (batch) and C (bulk) insert 10,000 objects instead of 100 (`BATCH_SIZE`). A durable commit costs ~8 ms, so with 100 objects per transaction B and C mostly measured that one commit. After B and after C an untimed step (`benchmarks/trim.py`, ObjectBox: `benchmarks/objectbox/trim.py`) deletes the newest 9,900 rows again, so D–K run on ~300 rows, as before; `LARGE_TABLE=1` skips it (D–K on ~20,100 rows).
- peewee's bulk insert runs all `insert_many()` chunks in one transaction (it committed each 100-row chunk on its own).
- SA ORM and SQLModel, sync and async, bulk insert with `bulk_save_objects()` (sync SQLModel and both async variants used `add_all()`, which inserts row by row).
- Piccolo and ormar split their bulk insert into chunks in one transaction (SQLite allows at most 32,766 variables per statement).
- SQLObject: Delete uses `destroySelf()` (the classmethod `delete()` committed every row on its own connection), Update: Whole sets both fields in one `UPDATE` (`set()`), Filter: Small uses a random offset like the other ORMs.
- SA ORM async and SQLModel async: Update and Delete merge the loaded objects with `load=False` (no `SELECT` per object inside the write transaction).
- Async ORMs with one SQLite connection per task (SA ORM async, SQLModel async, Piccolo, ormar) use a 60 s busy timeout (default 5 s); with the larger transactions they failed with `database is locked`.
- Warm-up mode, WAL databases (peewee, Tortoise ORM): after restoring the DB, `warmup.py` checkpoints the WAL and starts the next one with a no-op write. Each restore writes every page of the DB into the WAL; with the larger DBs after B and C (up to ~1,000 pages on Test 3) the WAL passed SQLite's auto-checkpoint threshold (1,000 pages) during measured runs, whose commit then wrote the WAL back to the DB file; and the first commit to a restarted WAL also syncs its header. Warm peewee J/K on Test 3 were ~40% slower than cold; Tortoise ORM's Delete ~20% (`superseded/warmup-wal/`).
- ObjectBox: the 5.0.0b1 release from TestPyPI (2026-10-13: local build `0ac38fa` of the same version).

## Environment

Linux x86_64 (AMD Ryzen 9 5950X, ext4 on NVMe), CPU frequency governor `performance` (boost on), 1-minute load average below 1 before each ORM × test run.
Benchmark code: this repo at the commit that added this directory. SQLite runs with `synchronous=FULL`.

## Versions

| Component | Version |
|-----------|---------|
| Python (uv's CPython build) | 3.14.6 |
| SQLite (bundled with Python) | 3.53.1 |
| Django | 6.1.2 |
| peewee | 4.5.3 |
| SQLAlchemy | 2.1.4 |
| SQLModel | 0.0.48 |
| SQLObject | 3.13.1 |
| Tortoise ORM | 1.1.8 |
| Piccolo | 1.36.0 |
| ormar | 0.26.0 |
| ObjectBox | 5.0.0b1 (TestPyPI: `objectbox` 5.0.0b1, `objectbox-api` 5.0.0b1, `objectbox-clib` 5.3.2; codegen on, no codegen cache) |
