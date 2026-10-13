# Raw results, 2026-10-13

`sqlite/` holds the data behind the cold SQLite tables and charts in the main README, `sqlite-warm/` the data behind the warm ones (`WARMUP=1`). They replace the results of `../2026-10-12/`.

- `run1` … `run5`: the raw `bench.sh` output of 5 full SQLite runs (all ORMs, Tests 1–3, 100 iterations), one `outfile<test>` per test model. Besides the `Rows/sec` lines they contain the ORMs' warnings (e.g. Django's system check).
- `median/`: the median of the 5 runs for each ORM and operation. The README tables and `images/sqlite_*.png` (cold) and `images/sqlite_warm_*.png` (warm) are generated from these files.

All ORMs ran together in each run: the 5 cold runs first, then the 5 warm runs.

## Changes since 2026-10-12

- Only persisting is timed: insert tests create the unsaved objects before the timer starts, update tests choose the new values before it (see "Timed section" in `AGENTS.md`).
- Right before the timer starts, each test runs `gc.collect()` and `gc.freeze()`.
- CPU frequency governor `performance` (2026-10-12: `schedutil`).

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
| ObjectBox | 5.0.0b1 (unreleased; objectbox-python branch `fast-flatbuffers-builder` @ `fc7c0be`, codegen on, no codegen cache) |
