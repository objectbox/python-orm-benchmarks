# Raw results, 2026-10-12

`sqlite/` holds the data behind the cold SQLite tables and charts in the main README, `sqlite-warm/` the data behind the warm ones (`WARMUP=1`).

- `run1` … `run5`: the raw `bench.sh` output of 5 full SQLite runs (all ORMs, Tests 1–3, 100 iterations), one `outfile<test>` per test model. Besides the `Rows/sec` lines they contain the ORMs' warnings (e.g. Django's system check).
- `median/`: the median of the 5 runs for each ORM and operation. The README tables and `images/sqlite_*.png` are generated from these files.

Sync SQLModel (`SQLModel`) was added later the same day: its 5 runs were done separately and appended to each `run<n>/outfile<test>`, after the results of the other ORMs.

ObjectBox was rerun later the same day with a newer build (`fc7c0be`, see Versions): its 5 runs replace the ObjectBox lines in each `run<n>/outfile<test>` and are appended at the end. The results of the earlier build (`0c8b3e6`, which imported numpy at startup and whose idle OpenBLAS threads slowed down the first operations) are kept in `superseded/objectbox-0c8b3e6/`.

`sqlite-warm/` has the same layout: 5 full runs with `WARMUP=1` (each operation runs once untimed, the DB is restored, then the operation is timed; see `benchmarks/warmup.py`) and their medians, generated as `images/sqlite_warm_*.png` and the tables under "Results: SQLite, warm". The ObjectBox results in it come from 5 separate warm runs: in the first full runs, the warm-up restore wrote the ObjectBox store files without syncing them, so the measured run's first commit also flushed them (e.g. Delete at half speed). That was fixed (the restored files are synced) before the ObjectBox rerun.

## Environment

Linux x86_64 (AMD Ryzen 9 5950X, ext4 on NVMe).
Benchmark code: this repo at commit `bfed9cf` for the cold runs of all ORMs except ObjectBox, `9eb238d` for the ObjectBox cold runs (`OBX_CODEGEN_CACHE` unset), and the commit that added `sqlite-warm/` for the warm runs.

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
