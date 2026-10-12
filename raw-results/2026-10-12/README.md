# Raw results, 2026-10-12

`sqlite/` holds the data behind the SQLite tables and charts in the main README.

- `run1` … `run5`: the raw `bench.sh` output of 5 full SQLite runs (all ORMs, Tests 1–3, 100 iterations), one `outfile<test>` per test model. Besides the `Rows/sec` lines they contain the ORMs' warnings (e.g. Django's system check).
- `median/`: the median of the 5 runs for each ORM and operation. The README tables and `images/sqlite_*.png` are generated from these files.

Sync SQLModel (`SQLModel`) was added later the same day: its 5 runs were done separately and appended to each `run<n>/outfile<test>`, after the results of the other ORMs.

## Environment

Linux x86_64 (AMD Ryzen 9 5950X, ext4 on NVMe).
Benchmark code: this repo at commit `bfed9cf`.

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
| ObjectBox | 5.0.0b1 (unreleased) |
