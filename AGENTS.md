# AGENTS.md

This file provides guidance to AI coding agents working with code in this repository.

## What this is

A benchmark suite comparing Python ORMs (Django, peewee, SQLAlchemy sync and async, SQLObject, Tortoise ORM, Piccolo, ormar, SQLModel) on SQLite, PostgreSQL and MySQL, plus the embedded object database ObjectBox (SQLite runs only). There is no test suite; the "tests" are benchmark operations. `README.md` holds the published results tables and charts.

## Commands

```sh
uv venv --python 3.14 && source .venv/bin/activate
uv pip install --no-sources --find-links wheels -r pyproject.toml
```

`objectbox==5.0.0b1` is an unreleased beta that is not on PyPI, so its wheels must be in `wheels/` (gitignored, not committed). They are built from objectbox-python branch `fast-flatbuffers-builder` @ `0c8b3e6` (not pushed), which includes the experimental codegen for puts and reads:
```sh
mkdir -p wheels && cp ~/dev/objectbox-python/dist/*.whl wheels/
```
`make build` in objectbox-python replaces `dist/`. The version string doesn't change between builds, so reinstall with `uv pip install --force-reinstall --no-deps wheels/objectbox-5.0.0b1-py3-none-any.whl`. Wheels built from other branches also carry version 5.0.0b1 but lack the codegen. Expected sha256 for Linux x86_64: `objectbox-5.0.0b1-py3-none-any.whl` `0b0129424b60e485ceca20a264e01049ef8df45393546cb72216c938b90dd9f2`, `objectbox_clib-5.3.2-py3-none-manylinux_2_28_x86_64.whl` `735ff58e7d71212922378bbc9d076b5ad09d1391b6874fdff448849af65e6ab0`.

Use Python 3.14 to match the published results. Without `--python`, uv picks whatever interpreter it already has, which may be older. SQLite is the version bundled with the Python build (3.53.1 with uv's CPython 3.14.6), not a pip package; `smoke.py` prints the version in use. pydantic is held below 2.14 by ormar's version constraint.

`uv pip install -e .` (and so `make deps`) fails: hatchling finds no package to build. `--no-sources` skips the `[tool.uv.sources]` entry that points `tortoise-orm` at a local macOS path (`/Users/abondar/...`).

Lint/format (black line length 100, flake8, isort, bandit; applies to `benchmarks/`):
```sh
make style    # isort + black
make check    # black --check, flake8, bandit
```

Run benchmarks. Shell scripts read their config from env vars: `DBTYPE` (`sqlite` (default) | `postgres` | `mysql`), `PASSWORD`, `PGPORT`, `MYPORT`, `TEST` (1|2|3), `ITERATIONS`, `CONCURRENTS` (async ORMs, default 10), `UVLOOP`, `OBX_CODEGEN` (ObjectBox experimental codegen, `1` (default) | `0`; with `0` the results are labeled "ObjectBox (no codegen)").
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

Run a single ORM / single test model:
```sh
cd benchmarks && TEST=2 ITERATIONS=100 DBTYPE=sqlite sh tortoise/bench.sh
```
Run a single operation with a sync ORM: `cd benchmarks/peewee && ../db.sh && python -m set_up && python -m test_d`. Async ORMs run every operation in one process through `bench.py`, so to run a single op you edit `bench.py`.

DB setup (`benchmarks/db.sh`): SQLite uses `/tmp/db.sqlite3`. Postgres needs `psql` reaching `127.0.0.1` as user `postgres`. MySQL expects a Docker container named `bench-mysql`. Each run drops and recreates database `tbench`.

## Architecture

- **One directory per ORM** under `benchmarks/<orm>/`, each with `models.py`, `bench.sh` and `test_a.py` … `test_k.py`, one file per operation (A = single insert … K = delete; the operation table is in README.md). Some ORMs leave out operations they don't support (e.g. SQLObject has no C/G/H, Pony has no C).
- **Test model selection**: every `models.py` reads `TEST` from the env at import time and defines a different `Journal` model for it: 1 = simple 4-field model, 2 = self-FK + M2M, 3 = wide model with 32+ fields. A model change has to be made in all ORM directories so the comparison stays fair.
- **Sync vs async runners**: sync ORMs (django, peewee, sqlobject, pony, sqlalchemy) run each `test_*.py` as a separate `python -m` process from `bench.sh`, after a `set_up.py`/migrate step. Async ORMs (tortoise, piccolo, ormar, sqlalchemy_async, sqlmodel) have a `bench.py` that builds the DB URL from env, creates the schema and awaits each test module's `runtest(loopstr)`. Each async test fans out across `CONCURRENTS` coroutines with `asyncio.gather`.
- **Output contract**: every test prints exactly one line, `"<ORM Name>, <Letter>: Rows/sec: <float>"`. `benchmarks/present.py` (stdin → table with geometric mean and best ORM), `generate_tables.py` and `generate_charts.py` all parse that format with regexes, so keep it exact. The ORM display name must also match the `ORM_ORDER`/`ORM_COLORS` lists in the generator scripts.
- **Which ORMs run**: `benchmarks/bench.sh` lists the ORMs explicitly for each test. `pony/` exists but is not in the list. Sync `sqlalchemy/` prints as "SA ORM", `sqlalchemy_async/` as "SA ORM async". To add an ORM, create its directory, add it to all three test blocks in `bench.sh`, and add it to the ORM lists in `generate_tables.py`/`generate_charts.py` and to README.md.
- **ObjectBox** (`benchmarks/objectbox/`, sync layout) is not a SQL ORM: its `bench.sh` exits immediately for `DBTYPE=postgres`/`mysql`, and it doesn't use `db.sh`. `set_up.py` wipes `/tmp/objectbox-bench`, which also holds `objectbox-model.json`, so each `TEST` starts with a fresh schema. Differences from the SQL ORMs: no relations in the Python binding (Test 2 uses indexed id properties), no NULL or per-property defaults (Test 3: `new_journal()` sets defaults, "nullable" columns stay unset), decimals stored as strings, JSON as a JSON string via the `put`/`find`/`get`/`get_all` helpers in `models.py` (Flex decodes ~40x slower than `json.loads`), no G/H (no projection API), and J writes the whole object. Beta quirk: `Query.offset()`/`limit()` don't return the query, so don't chain them.
- **Results pipeline**: `bench.sh` writes `benchmarks/outfile{1,2,3}` and appends to `benchmarks/results`. `generate_tables.py` (markdown tables for README.md) and `generate_charts.py` (PNGs in `images/`) read from `/tmp/{pg,mysql,sqlite}_outfile{1,2,3}`, so the outfiles have to be copied/renamed there for each DB type before you run them.
