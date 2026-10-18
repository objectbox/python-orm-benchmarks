# AGENTS.md

This file provides guidance to AI coding agents working with code in this repository.

## What this is

A benchmark suite comparing Python ORMs (Django, peewee, SQLAlchemy and SQLModel sync and async, SQLObject, Tortoise ORM, Piccolo, ormar) on SQLite, PostgreSQL and MySQL, plus the embedded object database ObjectBox (SQLite runs only). There is no test suite; the "tests" are benchmark operations. `README.md` holds the published results tables and charts.

## Commands

```sh
uv venv --python 3.14 && source .venv/bin/activate
uv pip install --no-deps --index-url https://test.pypi.org/simple/ objectbox==5.0.0b1 objectbox-api==5.0.0b1 objectbox-clib==5.3.2
uv pip install --no-sources -r pyproject.toml
```

`objectbox==5.0.0b1` is a beta that is only on TestPyPI, so it's installed first, on its own: with `--no-deps` and TestPyPI as the only index, so no other package comes from TestPyPI; the second command then finds it installed. Since 5.0, `objectbox` is a metapackage: the Python code is in `objectbox-api`, the C library in `objectbox-clib`. Upgrading a venv that has an older `objectbox` (4.x, or a local 5.0.0b1 build that still contains the code) in place breaks `import objectbox`, so `uv pip uninstall objectbox` first. Its experimental codegen for puts and reads is on by default. Expected sha256: `objectbox-5.0.0b1-py3-none-any.whl` `aa787fd532cd342dc99ddb0ab2373358afc3bdc964629f647a38a745d7b9d006`, `objectbox_api-5.0.0b1-py3-none-any.whl` `95a908d42e5f6c7babb3183dc2abdbf9f493e056f894ef9d032cf942f1e9f797`, `objectbox_clib-5.3.2-py3-none-manylinux_2_28_x86_64.whl` `fd585a88bbb473bb976e53c3a40afe8aad88e1c1eff61b1c7945a6dd8a693dc9` (same `libobjectbox.so` as the earlier local builds).

The published SQLite results were measured with local builds of objectbox-python branch `fast-flatbuffers-builder` @ `0ac38fa` (see `raw-results/`). The TestPyPI release renamed `Query.set_parameter_int()` to `set_parameter()` (used by D/E), so the tests no longer run with those builds; a quick check (4 interleaved runs each) found the release within ±2% of `0ac38fa` overall.

Use Python 3.14 to match the published results. Without `--python`, uv picks whatever interpreter it already has, which may be older. SQLite is the version bundled with the Python build (3.53.1 with uv's CPython 3.14.6), not a pip package; `smoke.py` prints the version in use. pydantic is held below 2.14 by ormar's version constraint.

`uv pip install -e .` (and so `make deps`) fails: hatchling finds no package to build. `--no-sources` skips the `[tool.uv.sources]` entry that points `tortoise-orm` at a local macOS path (`/Users/abondar/...`).

Lint/format (black line length 100, flake8, isort, bandit; applies to `benchmarks/`):
```sh
make style    # isort + black
make check    # black --check, flake8, bandit
```

Run benchmarks. Shell scripts read their config from env vars: `DBTYPE` (`sqlite` (default) | `postgres` | `mysql`), `PASSWORD`, `PGPORT`, `MYPORT`, `TEST` (1|2|3), `ITERATIONS`, `CONCURRENTS` (async ORMs, default 10), `UVLOOP`, `OBX_CODEGEN` (ObjectBox experimental codegen, `1` (default) | `0`; with `0` the results are labeled "ObjectBox (no codegen)"), `OBX_CODEGEN_CACHE` (ObjectBox: directory to cache the compiled codegen in across processes, off by default; results are labeled "ObjectBox (codegen cache)"), `WARMUP` (`0` (default) | `1`, SQLite only, see below).
```sh
cd benchmarks && sh bench.sh          # all ORMs, Tests 1-3, 100 iterations ("full" = 1000, "extra" = 10000)
cd benchmarks && sh bench_all.sh      # sqlite + postgres + mysql
make benchmark_sqlite | benchmark_postgres | benchmark_mysql
```

Smoke test (SQLite only; there is no other test suite). It runs each ORM in `bench.sh` for Tests 1-3 and fails when an expected `Rows/sec` line is missing or error output appears. Don't rely on exit codes: the sync `bench.sh` scripts keep going after a failing step.
```sh
.venv/bin/python benchmarks/smoke.py                 # all ORMs, tests 1-3, 100 iterations (~2 min)
.venv/bin/python benchmarks/smoke.py -t 1 -v peewee  # one ORM/test, print output of failures
```

Warm-up mode (`WARMUP=1`, SQLite only; exits with an error for other DB types): `benchmarks/warmup.py` runs each operation once untimed (output discarded), restores the DB to the state before it (SQLite backup API; ObjectBox: in-memory copy of the store files, written back and fsynced, then `models.reopen()`), then runs and times it in the same process. Sync `bench.sh` scripts run `python ../warmup.py <module>` instead of `python -m <module>` through their `run()` function; async `bench.py` scripts wrap each test in `await warm(test_x.runtest, loopstr)`. Without `WARMUP=1` both paths behave as before ("cold"). `WARMUP_CHECK=1` prints to stderr, per operation, whether row counts and highest IDs after the measured run match the warm-up run. `smoke.py -w` runs the smoke test in warm-up mode. Reopening an ObjectBox store re-syncs the model, which drops the compiled codegen, so `reopen()` carries over the binding internals `box._entity._fast_builder`/`_codegen_builder`; a wheel that renames them makes warm ObjectBox runs fail with an AttributeError, and one that keeps the codegen elsewhere would recompile it inside the timed run. PG/MySQL would need a restore of their own (e.g. `TRUNCATE … RESTART IDENTITY`).

Run a single ORM / single test model:
```sh
cd benchmarks && TEST=2 ITERATIONS=100 DBTYPE=sqlite sh tortoise/bench.sh
```
Run a single operation with a sync ORM: `cd benchmarks/peewee && ../db.sh && python -m set_up && python -m test_d`. Async ORMs run every operation in one process through `bench.py`, so to run a single op you edit `bench.py`.

DB setup (`benchmarks/db.sh`): SQLite uses `/tmp/db.sqlite3`. Postgres needs `psql` reaching `127.0.0.1` as user `postgres`. MySQL expects a Docker container named `bench-mysql`. Each run drops and recreates database `tbench`.

## Architecture

- **One directory per ORM** under `benchmarks/<orm>/`, each with `models.py`, `bench.sh` and `test_a.py` … `test_k.py`, one file per operation (A = single insert … K = delete; the operation table is in README.md). Some ORMs leave out operations they don't support (e.g. SQLObject has no C/G/H, Pony has no C).
- **Test model selection**: every `models.py` reads `TEST` from the env at import time and defines a different `Journal` model for it: 1 = simple 4-field model, 2 = self-FK + M2M, 3 = wide model with 32+ fields. A model change has to be made in all ORM directories so the comparison stays fair.
- **Sync vs async runners**: sync ORMs (django, peewee, sqlobject, pony, sqlalchemy, sqlmodel_sync, objectbox) run each `test_*.py` as a separate process from `bench.sh` (`run test_x`: `python -m test_x`, or `../warmup.py` with `WARMUP=1`), after a `set_up.py`/migrate step. Async ORMs (tortoise, piccolo, ormar, sqlalchemy_async, sqlmodel) have a `bench.py` that builds the DB URL from env, creates the schema and awaits each test module's `runtest(loopstr)`. Each async test fans out across `CONCURRENTS` coroutines with `asyncio.gather`.
- **Timed section**: only persisting is timed. Insert tests (A/B/C) create the unsaved objects before `start = time.time()` and the timed loop only saves them (e.g. `obj.save(force_insert=True)` instead of `objects.create(...)`); update tests (I/J) choose the new values before the timer. SQLObject inserts in its constructor, so only its field values are prepared; peewee's C prepares row tuples. Async tests build one list per concurrent task inside `runtest()` (not at module level), so the warm-up run gets fresh objects. Right before the timer, every test calls `gc.collect()` and `gc.freeze()`, so leftovers from the preparation (or the warm-up run) aren't collected while timed and existing objects stay out of collections. Keep this when adding an ORM or changing a test.
- **Output contract**: every test prints exactly one line, `"<ORM Name>, <Letter>: Rows/sec: <float>"`. `benchmarks/present.py` (stdin → table with geometric mean and best ORM), `generate_tables.py` and `generate_charts.py` all parse that format with regexes, so keep it exact. The ORM display name must also match the `ORM_ORDER`/`ORM_COLORS` lists in the generator scripts.
- **Which ORMs run**: `benchmarks/bench.sh` lists the ORMs explicitly for each test. `pony/` exists but is not in the list. Sync `sqlalchemy/` prints as "SA ORM", `sqlalchemy_async/` as "SA ORM async"; likewise `sqlmodel_sync/` as "SQLModel" and `sqlmodel/` as "SQLModel async". To add an ORM, create its directory, add it to all three test blocks in `bench.sh`, and add it to the ORM lists in `generate_tables.py`/`generate_charts.py` and to README.md.
- **ObjectBox** (`benchmarks/objectbox/`, sync layout) is not a SQL ORM: its `bench.sh` exits immediately for `DBTYPE=postgres`/`mysql`, and it doesn't use `db.sh`. `set_up.py` wipes `/tmp/objectbox-bench`, which also holds `objectbox-model.json`, so each `TEST` starts with a fresh schema. Differences from the SQL ORMs: no relations in the Python binding (Test 2 uses indexed id properties), no NULL or per-property defaults (Test 3: `new_journal()` sets defaults, "nullable" columns stay unset), decimals stored as strings, JSON as a JSON string via the `put`/`find`/`get`/`get_all` helpers in `models.py` (Flex decodes ~40x slower than `json.loads`), no G/H (no projection API), and J writes the whole object.
- **Results pipeline**: `bench.sh` writes `benchmarks/outfile{1,2,3}` and appends to `benchmarks/results`. `generate_tables.py` (markdown tables for README.md) and `generate_charts.py` (PNGs in `images/`) read from `/tmp/{pg,mysql,sqlite}_outfile{1,2,3}`, so the outfiles have to be copied/renamed there for each DB type before you run them. `raw-results/<date>/` keeps the raw outfiles and medians behind the published tables (`.gitignore` ignores `outfile*` except there).
