# AGENTS.md

This file provides guidance to AI coding agents working with code in this repository.

## What this is

A benchmark suite comparing Python ORMs (Django, peewee, SQLAlchemy and SQLModel sync and async, SQLObject, Tortoise ORM, Piccolo, ormar) on SQLite, PostgreSQL and MySQL, plus the embedded object database ObjectBox (SQLite runs only).
There is no test suite; the "tests" are benchmark operations.
The focus is on embedded databases: `README.md` holds the published SQLite/ObjectBox results tables and charts; the older PostgreSQL/MySQL results are in `postgres-mysql.md`.

## Commands

```sh
uv venv --python 3.14 && source .venv/bin/activate
uv pip install --no-sources -r pyproject.toml
```

Since 5.0, `objectbox` (5.0.0, from PyPI) is a metapackage: the Python code is in `objectbox-api`, the C library in `objectbox-clib`. Upgrading a venv that has an older `objectbox` (4.x, or a local 5.0 build that still contains the code) in place breaks `import objectbox`, so `uv pip uninstall objectbox` first. Its experimental codegen for puts and reads is on by default. Expected sha256 (PyPI): `objectbox-5.0.0-py3-none-any.whl` `1ab4bc3f87f297dcd96ecf6009448601844e80ae37dde67cadb53efaf00d8f6d`, `objectbox_api-5.0.0-py3-none-any.whl` `62e7d942e6bd39ab6c24cb94e23cb10d90976110743da40fd3846fccb8200d7a`, `objectbox_clib-5.3.2-py3-none-manylinux_2_28_x86_64.whl` `e1e7ae36fea6a941dffee8a84abd34d1785d164efc3ebbecc024f7ff34ab9d76` (its `libobjectbox.so` is the same as in the TestPyPI wheels and the earlier local builds).

The published SQLite results (`raw-results/2026-10-18/`) were measured with the 5.0.0b1 beta from TestPyPI (`objectbox`/`objectbox-api` 5.0.0b1, same `objectbox-clib` 5.3.2). The results before them (`raw-results/2026-10-13/`) used local builds of objectbox-python branch `fast-flatbuffers-builder` @ `0ac38fa`, which no longer run the tests: the release renamed `Query.set_parameter_int()` to `set_parameter()` (used by D/E).

Use Python 3.14 to match the published results. Without `--python`, uv picks whatever interpreter it already has, which may be older. SQLite is the version bundled with the Python build (3.53.1 with uv's CPython 3.14.6), not a pip package; `smoke.py` prints the version in use. pydantic is held below 2.14 by ormar's version constraint.

`uv pip install -e .` (and so `make deps`) fails: hatchling finds no package to build. `--no-sources` skips the `[tool.uv.sources]` entry that points `tortoise-orm` at a local macOS path (`/Users/abondar/...`).

Lint/format (black line length 100, flake8, isort, bandit; applies to `benchmarks/`):
```sh
make style    # isort + black
make check    # black --check, flake8, bandit
```

Run benchmarks. Shell scripts read their config from env vars: `DBTYPE` (`sqlite` (default) | `postgres` | `mysql`), `PASSWORD`, `PGPORT`, `MYPORT`, `TEST` (1|2|3), `ITERATIONS`, `BATCH_SIZE` (objects per B/C insert, default 10000), `LARGE_TABLE` (`0` (default) | `1`, see below), `CONCURRENTS` (async ORMs, default 10), `UVLOOP`, `OBX_CODEGEN` (ObjectBox experimental codegen, `1` (default) | `0`; with `0` the results are labeled "ObjectBox (no codegen)"), `OBX_CODEGEN_CACHE` (ObjectBox: directory to cache the compiled codegen in across processes, off by default; results are labeled "ObjectBox (codegen cache)"), `WARMUP` (`0` (default) | `1`, SQLite only, see below).
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

Warm-up mode (`WARMUP=1`, SQLite only; exits with an error for other DB types): `benchmarks/warmup.py` runs each operation once untimed (output discarded), restores the DB to the state before it (SQLite backup API; in WAL mode (peewee, Tortoise ORM) it then checkpoints the WAL and starts a new one with a no-op write, so the measured run's commit neither runs the auto-checkpoint for the restored pages nor syncs a new WAL header, as in a cold run; ObjectBox: in-memory copy of the store files, written back and fsynced, then `models.reopen()`), then runs and times it in the same process. Sync `bench.sh` scripts run `python ../warmup.py <module>` instead of `python -m <module>` through their `run()` function; async `bench.py` scripts wrap each test in `await warm(test_x.runtest, loopstr)`. Without `WARMUP=1` both paths behave as before ("cold"). `WARMUP_CHECK=1` prints to stderr, per operation, whether row counts and highest IDs after the measured run match the warm-up run. `smoke.py -w` runs the smoke test in warm-up mode. Reopening an ObjectBox store re-syncs the model, which drops the compiled codegen, so `reopen()` carries over the binding internals `box._entity._fast_builder`/`_codegen_builder`; a wheel that renames them makes warm ObjectBox runs fail with an AttributeError, and one that keeps the codegen elsewhere would recompile it inside the timed run. PG/MySQL would need a restore of their own (e.g. `TRUNCATE … RESTART IDENTITY`).

Run a single ORM / single test model:
```sh
cd benchmarks && TEST=2 ITERATIONS=100 DBTYPE=sqlite sh tortoise/bench.sh
```
Run a single operation with a sync ORM: `cd benchmarks/peewee && ../db.sh && python -m set_up && python -m test_d`. Async ORMs run every operation in one process through `bench.py`, so to run a single op you edit `bench.py`.

DB setup (`benchmarks/db.sh`): SQLite uses `/tmp/db.sqlite3`. Postgres needs `psql` reaching `127.0.0.1` as user `postgres`. MySQL expects a Docker container named `bench-mysql`. Each run drops and recreates database `tbench`.

## Architecture

- **One directory per ORM** under `benchmarks/<orm>/`, each with `models.py`, `bench.sh` and `test_a.py` … `test_k.py`, one file per operation (A = single insert … K = delete; the operation table is in README.md). G/H (dict/tuple projections) are measured but not presented: `generate_tables.py`/`generate_charts.py` leave them out of the tables, charts and geometric means (`OP_ORDER`). Some ORMs leave out operations they don't support (e.g. SQLObject has no C/G/H, Pony has no C).
- **Test model selection**: every `models.py` reads `TEST` from the env at import time and defines a different `Journal` model for it: 1 = simple 4-field model, 2 = self-FK + M2M, 3 = wide model with 32+ fields. A model change has to be made in all ORM directories so the comparison stays fair.
- **Sync vs async runners**: sync ORMs (django, peewee, sqlobject, pony, sqlalchemy, sqlmodel_sync, objectbox) run each `test_*.py` as a separate process from `bench.sh` (`run test_x`: `python -m test_x`, or `../warmup.py` with `WARMUP=1`), after a `set_up.py`/migrate step. Async ORMs (tortoise, piccolo, ormar, sqlalchemy_async, sqlmodel) have a `bench.py` that builds the DB URL from env, creates the schema and awaits each test module's `runtest(loopstr)`. Each async test fans out across `CONCURRENTS` coroutines with `asyncio.gather`.
- **Timed section**: only persisting is timed. Insert tests (A/B/C) create the unsaved objects before `start = time.time()` and the timed loop only saves them (e.g. `obj.save(force_insert=True)` instead of `objects.create(...)`); update tests (I/J) choose the new values before the timer. SQLObject inserts in its constructor, so only its field values are prepared; peewee's C prepares row tuples. Async tests build one list per concurrent task inside `runtest()` (not at module level), so the warm-up run gets fresh objects. Right before the timer, every test calls `gc.collect()` and `gc.freeze()`, so leftovers from the preparation (or the warm-up run) aren't collected while timed and existing objects stay out of collections. Keep this when adding an ORM or changing a test.
- **Batch size and table size**: B and C insert `BATCH_SIZE` objects (default 10000; all other operations use `ITERATIONS`), so their transaction measures insert throughput instead of mostly one durable commit (~8 ms). D-K run on the whole table, so after B and C each `bench.sh`/`bench.py` calls an untimed trim step (`benchmarks/trim.py`, ObjectBox `objectbox/trim.py`; SQLite only) that deletes the newest `BATCH_SIZE - ITERATIONS` rows: D-K see ~300 rows, as before. Django's table is `simple_journal<TEST>`, so its `bench.sh` passes that name. `LARGE_TABLE=1` skips the trim: D-K then run on ~20,100 rows; these results are published separately ("large table").
- **Bulk insert (C)**: each ORM's fastest bulk path. SQLAlchemy/SQLModel (sync and async) use `bulk_save_objects()`; `session.add_all()` inserts one by one, like B. Only Django, Piccolo and ObjectBox set the new IDs on the objects; peewee inserts row tuples. Piccolo and ormar split their bulk insert into chunks inside one transaction: SQLite allows at most 32,766 variables per statement (Test 3 has ~36 columns).
- **SQLite journal mode**: peewee's `models.py` opens SQLite in WAL mode (taken over from the original benchmark; peewee itself sets none) and Tortoise ORM uses WAL by default; all other SQL ORMs use SQLite's default rollback journal. Both are durable with `synchronous=FULL`, but a WAL commit syncs one file: single inserts run ~3x faster (peewee with WAL off: 54 instead of 160 rows/sec), large transactions ~7%. A known caveat of the published results (README analysis); measuring all ORMs both ways is future work.
- **Async ORMs on SQLite**: each async test runs `CONCURRENTS` tasks with one transaction each; SA ORM async, SQLModel async, Piccolo and ormar open one SQLite connection per task, which wait for the write lock. Their SQLite connections use a 60 s busy timeout (default 5 s), otherwise large transactions fail with `database is locked`. Don't read rows inside a write transaction there (e.g. `session.merge(obj)` without `load=False`): a transaction that read first can't wait for the write lock: if another connection committed in between, SQLite fails it at once with `database is locked`.
- **Output contract**: every test prints exactly one line, `"<ORM Name>, <Letter>: Rows/sec: <float>"`. `benchmarks/present.py` (stdin → table with geometric mean and best ORM), `generate_tables.py` and `generate_charts.py` all parse that format with regexes, so keep it exact. The ORM display name must also match the `ORM_ORDER`/`ORM_COLORS` lists in the generator scripts.
- **Which ORMs run**: `benchmarks/bench.sh` lists the ORMs explicitly for each test. `pony/` exists but is not in the list. Sync `sqlalchemy/` prints as "SA ORM", `sqlalchemy_async/` as "SA ORM async"; likewise `sqlmodel_sync/` as "SQLModel" and `sqlmodel/` as "SQLModel async". To add an ORM, create its directory, add it to all three test blocks in `bench.sh`, and add it to the ORM lists in `generate_tables.py`/`generate_charts.py` and to README.md.
- **ObjectBox** (`benchmarks/objectbox/`, sync layout) is not a SQL ORM: its `bench.sh` exits immediately for `DBTYPE=postgres`/`mysql`, and it doesn't use `db.sh`. `set_up.py` wipes `/tmp/objectbox-bench`, which also holds `objectbox-model.json`, so each `TEST` starts with a fresh schema. Differences from the SQL ORMs: no relations in the Python binding (Test 2 uses indexed id properties), no NULL or per-property defaults (Test 3: `new_journal()` sets defaults, "nullable" columns stay unset), decimals stored as strings, JSON as a JSON string via the `put`/`find`/`get`/`get_all` helpers in `models.py` (Flex decodes ~40x slower than `json.loads`), no G/H (no projection API), and J writes the whole object.
- **Results pipeline**: `bench.sh` writes `benchmarks/outfile{1,2,3}` and appends to `benchmarks/results`. The published SQLite results are made with `tools/` (see "Publishing results"). `generate_tables.py`/`generate_charts.py` hold the table and chart functions; run as scripts, they read `/tmp/{pg,mysql,sqlite}_outfile{1,2,3}` (the older PG/MySQL flow). The per-test charts use a log scale (rows/sec span ~50 to ~1,000,000), the summary charts a linear one. `raw-results/<date>/` keeps the raw outfiles and medians behind the published tables (`.gitignore` ignores `outfile*` except there).

## Publishing results

The README, `large-table.md` and `images/sqlite*.png` come from `raw-results/<date>/` (SQLite and ObjectBox only):

```sh
PATH=$PWD/.venv/bin:$PATH tools/run_sqlite.sh raw-results/<date> | tee run.log   # 4 modes x 5 runs, ~7 h
for m in sqlite sqlite-warm sqlite-large sqlite-large-warm; do .venv/bin/python tools/median.py raw-results/<date>/$m; done
.venv/bin/python tools/publish.py raw-results/<date>   # charts, geomean tables and detailed tables
```

- Settings: CPU frequency governor `performance`, `ITERATIONS=100`, `BATCH_SIZE=10000`; `run_sqlite.sh` waits for a 1-minute load average below 1 before each ORM x test. Don't run anything else on the machine meanwhile, and don't change the working tree: each ORM x test runs the current code.
- Modes: `sqlite` (cold), `sqlite-warm`, `sqlite-large` and `sqlite-large-warm`; each published value is the median of 5 full runs. The log line per ORM x test must show `rows 11` (SQLObject 8, ObjectBox 9) and no `TIMEOUT`; "non-result lines" are warnings (Django, Tortoise ORM) or errors, check them.
- `publish.py` replaces only the tables; update the numbers quoted in the README's text (analysis, key takeaways), the environment note and `raw-results/<date>/README.md` (what changed, environment, versions) by hand. `tools/median.py` prints the widest run-to-run spreads: mention bimodal operations.
- Rerunning some ORMs (e.g. after a fix that only affects them): `ORMS="peewee tortoise" MODES=... tools/run_sqlite.sh <tmp-dir>`, then, per outfile, drop their lines and append the new ones, move the replaced lines to `raw-results/<date>/superseded/<reason>/` and say so in that directory's README.
- `blog-post.md` is a local draft (excluded via `.git/info/exclude`); don't commit it.

## Lessons from earlier runs

- Warm slower than cold for an operation is a red flag: the warm-up restore left work for the measured run. It happened twice: ObjectBox store files restored without fsync (the measured commit flushed them), and the WAL of peewee/Tortoise ORM full of restored pages (the measured commit ran the checkpoint).
- Some operations alternate between two levels from run to run, so a 5-run median can land on either (Tortoise ORM's large-table Test 3 updates/deletes; ObjectBox 5.0.0's cold Update: Whole, ~21k or ~40-57k rows/sec on Tests 1/2). Check `tools/median.py`'s spreads.
- File growth costs: rows deleted by the trim leave free space that later writes reuse; ObjectBox's update commits got cheaper (fdatasync ~1.7 instead of ~6.2 ms when the data file grows), so Update: Whole/Partial on Test 1 got 1.3x/1.9x faster than with `BATCH_SIZE=100`.
- Check how a test uses its ORM before blaming the ORM: SQLObject's classmethod `delete()` committed every row on its own connection (use `destroySelf()`), assigning attributes one by one sends one `UPDATE` each (use `set()`), peewee's `insert_many()` chunks each committed on their own (wrap in `db.atomic()`), `session.add_all()` inserts row by row.

## Open items

- ObjectBox: the published results were measured with 5.0.0b1; 5.0.0 (installed now, same C library) was within a few percent in a 4-round check, except cold Update: Whole (bimodal, see above). Rerunning ObjectBox in all 4 modes with 5.0.0 is pending.
- Test 2 Delete on the large table is slow for SA ORM, Tortoise ORM, Piccolo, ormar and Django (1,100-2,400 rows/sec); SA ORM's self-referencing `parent_id` has no index. A schema change means rerunning those ORMs in all modes.
- `make check`/`make style` fail at their `deps` step (`uv pip install -e .`); run black/flake8/isort/bandit directly (e.g. via `uvx`). Black flags some older files.
