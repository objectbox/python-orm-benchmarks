# Python Embedded Database Benchmarks: ObjectBox and SQLite

Performance benchmarks of embedded databases in Python: the object database [ObjectBox](https://github.com/objectbox/objectbox-python) and SQLite, accessed through popular Python ORMs. Everything runs in-process on local storage, without a database server.

Older results for PostgreSQL and MySQL (SQL ORMs only, earlier benchmark version, different machine) are in [postgres-mysql.md](postgres-mysql.md).

Higher is better: rows (objects) per second, as the geometric mean over the operations of each test that the ORM or database supports (ObjectBox and SQLObject leave out a few, see [Setup](#setup)). Each value is the median of 5 full runs.

## Overall results

### Cold

Sync ORMs and ObjectBox run each operation in a fresh process (async ORMs run all operations in one), so the timed part includes one-time costs such as opening the connection, compiling the first statements and filling caches.

![ObjectBox and SQLite Summary](images/sqlite_summary.png)

### Warm

Each operation first runs once untimed in the same process, the database is restored to its state before that run, and then the operation is timed (see [Detailed results: warm](#detailed-results-warm)).

![ObjectBox and SQLite Summary, warm](images/sqlite_warm_summary.png)

Geometric means, cold vs. warm:

| Database / ORM | Test 1 cold | Test 1 warm | Test 2 cold | Test 2 warm | Test 3 cold | Test 3 warm |
|-----|------------:|------------:|------------:|------------:|------------:|------------:|
| ObjectBox | 30,568 | **36,380** (×1.19) | 30,001 | **35,298** (×1.18) | 16,849 | **20,883** (×1.24) |
| Django | 11,118 | 12,987 (×1.17) | 9,751 | 11,200 (×1.15) | 6,354 | 7,223 (×1.14) |
| peewee | 21,659 | 26,324 (×1.22) | 20,732 | 24,559 (×1.18) | 10,218 | 11,284 (×1.10) |
| SA ORM | 13,338 | 16,392 (×1.23) | 9,831 | 13,349 (×1.36) | 8,822 | 11,285 (×1.28) |
| SA ORM async | 1,946 | 1,974 (×1.01) | 1,837 | 1,862 (×1.01) | 1,268 | 1,291 (×1.02) |
| SQLObject | 3,829 | 4,242 (×1.11) | 3,752 | 4,191 (×1.12) | 2,872 | 3,236 (×1.13) |
| Tortoise ORM | 7,821 | 8,085 (×1.03) | 8,059 | 7,586 (×0.94) | 5,590 | 5,605 (×1.00) |
| Piccolo | 2,059 | 2,027 (×0.98) | 1,992 | 2,001 (×1.00) | 1,231 | 1,219 (×0.99) |
| ormar | 1,692 | 1,717 (×1.01) | 1,632 | 1,655 (×1.01) | 1,059 | 1,075 (×1.02) |
| SQLModel | 13,042 | 16,463 (×1.26) | 12,861 | 16,521 (×1.28) | 8,640 | 10,729 (×1.24) |
| SQLModel async | 1,886 | 1,950 (×1.03) | 1,836 | 1,951 (×1.06) | 1,211 | 1,229 (×1.01) |

---

## Setup

**Tested:**

| Database / ORM | Type | Driver |
|----------------|------|--------|
| [ObjectBox](https://github.com/objectbox/objectbox-python) | sync | embedded (own storage engine) |
| [Django](https://www.djangoproject.com/) | sync | sqlite3 |
| [peewee](https://github.com/coleifer/peewee) | sync | sqlite3 |
| [SQLAlchemy ORM](http://www.sqlalchemy.org/) ("SA ORM") | sync | sqlite3 |
| [SQLAlchemy ORM (async)](http://www.sqlalchemy.org/) | async | aiosqlite |
| [SQLObject](https://github.com/sqlobject/sqlobject) | sync | sqlite3 |
| [Tortoise ORM](https://github.com/tortoise/tortoise-orm) | async | aiosqlite |
| [Piccolo](https://github.com/piccolo-orm/piccolo) | async | aiosqlite |
| [ormar](https://github.com/collerek/ormar) | async | aiosqlite |
| [SQLModel](https://github.com/tiangolo/sqlmodel) | sync | sqlite3 |
| [SQLModel (async)](https://github.com/tiangolo/sqlmodel) | async | aiosqlite |

> **Environment:** Python 3.14.6, SQLite 3.53.1 (bundled with uv's CPython build), Linux x86_64 (AMD Ryzen 9 5950X, ext4 on NVMe), 100 iterations per operation, CPU frequency governor `performance`, 1-minute load average below 1 before each ORM run. Each value is the median of 5 full runs (2026-10-13; ObjectBox: 5 runs of its own with a newer build on 2026-10-14). SQLite runs with `synchronous=FULL` (its compiled-in default), so every committed transaction is synced to disk, as with ObjectBox.
>
> ObjectBox is an embedded object database with its own storage engine, not an ORM on top of SQL. It uses the 5.0.0b1 beta (on TestPyPI) with its experimental FlatBuffers codegen for writes and reads enabled (`OBX_CODEGEN=0` disables it). Differences to the SQL ORMs: Test 2 uses plain indexed ids (the Python binding has no relations), Test 3 stores decimals as strings, JSON as JSON strings (like the SQL ORMs store it as text) and leaves "nullable" columns unset (no NULL support), Filter: dict/tuple are not supported (no projection API), and Update: Partial writes the whole object. Its geometric mean covers 9 operations.

### Operations

| Code | Operation | Description |
|------|-----------|-------------|
| A | Insert: Single | Insert one row at a time |
| B | Insert: Batch | Insert many rows in a single transaction |
| C | Insert: Bulk | Use bulk insert operations |
| D | Filter: Large | Fetch a large result set |
| E | Filter: Small | Fetch limit 20 with random offset |
| F | Get | Fetch a single row by primary key |
| G | Filter: dict | Fetch large result set as dicts |
| H | Filter: tuple | Fetch large result set as tuples |
| I | Update: Whole | Update all fields of a row |
| J | Update: Partial | Update a single field |
| K | Delete | Delete a single row |

Only persisting is timed: the insert operations create the unsaved objects before the timer starts, and the update operations choose the new values before it, so creating objects (including field defaults) and generating test data don't count. SQLObject inserts the row when it creates the object, so for SQLObject only the field values are prepared; peewee's bulk insert prepares row tuples and applies defaults while inserting. Right before the timer starts, each test runs `gc.collect()` and `gc.freeze()`, so garbage from the preparation isn't collected while timed.

### Test Models

**Test 1 — Simple model** (4 fields): `id`, `timestamp`, `level` (indexed), `text` (indexed)

**Test 2 — FK relations**: Same as Test 1, plus self-referential foreign key, reverse FK, and M2M relation

**Test 3 — Wide model** (32+ fields): Same as Test 1, plus 4 sets of 8 typed columns (float, smallint, int, bigint, char, text, decimal, json) — 2 with defaults, 2 nullable

---

## Detailed results: cold

SQLite on the local filesystem (`/tmp/db.sqlite3`), ObjectBox in `/tmp/objectbox-bench`. SQLite allows one writer at a time, so the benchmark is single-threaded; async ORMs pay overhead without a concurrency benefit. These are cold numbers; see [Detailed results: warm](#detailed-results-warm) for runs with a warm-up run before each operation.

### Test 1: Simple Model (4 fields)

![ObjectBox and SQLite Test 1](images/sqlite_test1.png)

| Operation | Django | peewee | SA ORM | SA ORM async | SQLObject | Tortoise ORM | Piccolo | ormar | SQLModel | SQLModel async | ObjectBox | Best |
|-----------|--------|--------|--------|--------------|-----------|--------------|---------|-------|----------|----------------|-----------|------|
| Insert: Single | 54 | 160 | 53 | 49 | 54 | 162 | 49 | 49 | 53 | 49 | **245** | ObjectBox |
| Insert: Batch | 2,869 | 5,901 | 4,116 | 221 | 3,482 | 1,493 | 221 | 219 | 3,271 | 221 | **11,470** | ObjectBox |
| Insert: Bulk | 3,384 | 7,417 | 3,471 | 221 | — | 1,597 | 222 | 323 | 3,252 | 221 | **11,646** | ObjectBox |
| Filter: Large | 163,785 | 219,912 | 179,315 | 42,766 | 77,852 | 81,178 | 46,554 | 28,937 | 171,616 | 43,344 | **466,051** | ObjectBox |
| Filter: Small | 52,070 | 82,205 | 56,233 | 21,496 | 66,533 | 52,032 | 21,985 | 12,661 | 49,489 | 19,997 | **261,538** | ObjectBox |
| Get | 7,055 | 11,655 | 8,151 | 3,532 | 14,765 | 8,236 | 2,452 | 1,528 | 9,418 | 3,463 | **152,465** | ObjectBox |
| Filter: dict | 230,363 | **306,489** | 173,066 | 42,957 | — | 98,329 | 55,320 | 35,905 | 132,139 | 38,184 | — | peewee |
| Filter: tuple | 238,213 | 308,027 | 265,692 | 58,120 | — | 93,615 | 53,080 | 36,046 | **392,309** | 50,022 | — | SQLModel |
| Update: Whole | 5,386 | 8,570 | 8,757 | 391 | 6,234 | 3,413 | 540 | 454 | 8,500 | 390 | **16,456** | ObjectBox |
| Update: Partial | 5,817 | 18,062 | 9,500 | 449 | 9,609 | 3,968 | 541 | 536 | 9,373 | 449 | **32,652** | ObjectBox |
| Delete | 5,956 | 22,753 | 9,947 | 449 | 54 | 4,005 | 542 | 538 | 9,919 | 449 | **71,453** | ObjectBox |
| **Geometric Mean** | 11,118 | 21,659 | 13,338 | 1,946 | 3,829 | 7,821 | 2,059 | 1,692 | 13,042 | 1,886 | **30,568** | **ObjectBox** |

### Test 2: FK Relations

![ObjectBox and SQLite Test 2](images/sqlite_test2.png)

| Operation | Django | peewee | SA ORM | SA ORM async | SQLObject | Tortoise ORM | Piccolo | ormar | SQLModel | SQLModel async | ObjectBox | Best |
|-----------|--------|--------|--------|--------------|-----------|--------------|---------|-------|----------|----------------|-----------|------|
| Insert: Single | 53 | 160 | 53 | 49 | 53 | 162 | 49 | 47 | 53 | 49 | **237** | ObjectBox |
| Insert: Batch | 2,824 | 5,878 | 3,119 | 220 | 3,366 | 1,513 | 221 | 219 | 3,259 | 220 | **11,376** | ObjectBox |
| Insert: Bulk | 3,377 | 7,394 | 3,490 | 220 | — | 1,598 | 221 | 266 | 3,238 | 221 | **11,607** | ObjectBox |
| Filter: Large | 149,386 | 187,374 | 146,770 | 41,817 | 75,359 | 83,536 | 42,500 | 27,577 | 163,680 | 37,405 | **454,470** | ObjectBox |
| Filter: Small | 54,094 | 81,615 | 38,404 | 21,975 | 64,355 | 52,755 | 19,009 | 11,595 | 49,750 | 19,526 | **259,101** | ObjectBox |
| Get | 6,779 | 10,834 | 6,688 | 3,419 | 14,455 | 9,020 | 2,266 | 1,488 | 9,020 | 3,356 | **147,169** | ObjectBox |
| Filter: dict | 208,769 | **277,505** | 137,061 | 40,323 | — | 103,951 | 54,267 | 37,536 | 132,333 | 36,620 | — | peewee |
| Filter: tuple | 219,620 | 285,101 | 198,056 | 46,667 | — | 99,150 | 52,300 | 34,442 | **376,903** | 48,105 | — | SQLModel |
| Update: Whole | 5,249 | 8,076 | 7,912 | 390 | 6,180 | 3,511 | 541 | 453 | 8,491 | 390 | **16,354** | ObjectBox |
| Update: Partial | 5,745 | 18,046 | 8,491 | 447 | 9,476 | 4,115 | 541 | 535 | 9,244 | 449 | **32,274** | ObjectBox |
| Delete | 1,963 | 22,881 | 2,091 | 332 | 53 | 4,025 | 541 | 538 | 9,923 | 448 | **68,703** | ObjectBox |
| **Geometric Mean** | 9,751 | 20,732 | 9,831 | 1,837 | 3,752 | 8,059 | 1,992 | 1,632 | 12,861 | 1,836 | **30,001** | **ObjectBox** |

### Test 3: Wide Model (32+ fields)

![ObjectBox and SQLite Test 3](images/sqlite_test3.png)

| Operation | Django | peewee | SA ORM | SA ORM async | SQLObject | Tortoise ORM | Piccolo | ormar | SQLModel | SQLModel async | ObjectBox | Best |
|-----------|--------|--------|--------|--------------|-----------|--------------|---------|-------|----------|----------------|-----------|------|
| Insert: Single | 53 | 158 | 53 | 49 | 53 | 161 | 49 | 48 | 52 | 49 | **213** | ObjectBox |
| Insert: Batch | 2,201 | 4,279 | 2,964 | 219 | 2,202 | 1,435 | 220 | 175 | 2,935 | 219 | **8,832** | ObjectBox |
| Insert: Bulk | 2,900 | 4,411 | 3,306 | 220 | — | 1,559 | 219 | 266 | 2,922 | 220 | **9,148** | ObjectBox |
| Filter: Large | 49,585 | 47,698 | 72,519 | 15,039 | 39,928 | 32,739 | 10,543 | 8,549 | 66,101 | 11,509 | **97,108** | ObjectBox |
| Filter: Small | 23,943 | 26,143 | 30,285 | 10,365 | 35,240 | 25,158 | 7,744 | 6,072 | 31,082 | 8,892 | **72,679** | ObjectBox |
| Get | 3,737 | 3,969 | 6,506 | 2,776 | 9,591 | 6,094 | 1,674 | 1,086 | 7,214 | 2,759 | **45,006** | ObjectBox |
| Filter: dict | 59,527 | **73,446** | 60,510 | 11,868 | — | 43,164 | 14,769 | 11,426 | 49,635 | 12,712 | — | peewee |
| Filter: tuple | 65,129 | 76,450 | 82,376 | 14,592 | — | 39,031 | 13,275 | 11,799 | **91,891** | 12,570 | — | SQLModel |
| Update: Whole | 3,841 | 3,871 | 8,022 | 389 | 6,031 | 3,286 | 537 | 387 | 7,875 | 389 | **13,150** | ObjectBox |
| Update: Partial | 5,268 | 17,387 | 8,702 | 446 | 9,158 | 4,061 | 536 | 535 | 8,664 | 447 | **21,846** | ObjectBox |
| Delete | 5,778 | 22,786 | 9,769 | 447 | 53 | 4,106 | 541 | 537 | 9,665 | 447 | **69,766** | ObjectBox |
| **Geometric Mean** | 6,354 | 10,218 | 8,822 | 1,268 | 2,872 | 5,590 | 1,231 | 1,059 | 8,640 | 1,211 | **16,849** | **ObjectBox** |

## Detailed results: warm

In the cold results, each sync ORM runs every operation in a fresh process, so the timed loop also pays one-time costs such as opening a lazily opened connection, compiling the first statements, filling the ORM's caches and, for ObjectBox, compiling its codegen (imports are never timed). These runs use the warm-up mode (`WARMUP=1`): each operation first runs once untimed in the same process (async ORMs: the same event loop), the database is restored to its state before that run (rows and ID sequences), and then the operation runs again and is timed. Same machine, versions and settings as the cold results; each value is the median of 5 full runs.

### Test 1: Simple Model (4 fields)

![ObjectBox and SQLite Test 1, warm](images/sqlite_warm_test1.png)

| Operation | Django | peewee | SA ORM | SA ORM async | SQLObject | Tortoise ORM | Piccolo | ormar | SQLModel | SQLModel async | ObjectBox | Best |
|-----------|--------|--------|--------|--------------|-----------|--------------|---------|-------|----------|----------------|-----------|------|
| Insert: Single | 53 | 161 | 53 | 49 | 54 | 163 | 49 | 49 | 53 | 49 | **245** | ObjectBox |
| Insert: Batch | 4,004 | 9,747 | 4,901 | 221 | 3,908 | 1,514 | 221 | 219 | 4,826 | 221 | **12,026** | ObjectBox |
| Insert: Bulk | 5,093 | **14,165** | 5,229 | 221 | — | 1,309 | 222 | 352 | 4,847 | 221 | 12,215 | peewee |
| Filter: Large | 172,458 | 228,104 | 211,780 | 44,184 | 86,531 | 84,205 | 45,059 | 30,096 | 192,426 | 44,280 | **509,904** | ObjectBox |
| Filter: Small | 59,954 | 94,960 | 62,115 | 22,358 | 78,105 | 52,400 | 21,010 | 12,290 | 59,653 | 19,974 | **346,181** | ObjectBox |
| Get | 7,278 | 12,283 | 8,825 | 3,545 | 16,385 | 9,158 | 2,394 | 1,529 | 10,463 | 3,512 | **219,081** | ObjectBox |
| Filter: dict | 249,829 | **326,329** | 184,271 | 42,780 | — | 105,672 | 52,363 | 34,339 | 142,605 | 43,639 | — | peewee |
| Filter: tuple | 262,401 | 327,825 | 315,559 | 54,954 | — | 102,306 | 52,020 | 34,053 | **471,270** | 53,162 | — | SQLModel |
| Update: Whole | 6,490 | 15,022 | 12,347 | 449 | 8,604 | 3,993 | 542 | 534 | 12,024 | 449 | **32,658** | ObjectBox |
| Update: Partial | 6,984 | 18,578 | 13,729 | 449 | 9,729 | 4,122 | 542 | 535 | 13,535 | 449 | **33,654** | ObjectBox |
| Delete | 7,298 | 23,752 | 14,737 | 449 | 54 | 4,159 | 543 | 537 | 14,680 | 450 | **72,978** | ObjectBox |
| **Geometric Mean** | 12,987 | 26,324 | 16,392 | 1,974 | 4,242 | 8,085 | 2,027 | 1,717 | 16,463 | 1,950 | **36,380** | **ObjectBox** |

### Test 2: FK Relations

![ObjectBox and SQLite Test 2, warm](images/sqlite_warm_test2.png)

| Operation | Django | peewee | SA ORM | SA ORM async | SQLObject | Tortoise ORM | Piccolo | ormar | SQLModel | SQLModel async | ObjectBox | Best |
|-----------|--------|--------|--------|--------------|-----------|--------------|---------|-------|----------|----------------|-----------|------|
| Insert: Single | 54 | 162 | 53 | 49 | 54 | 162 | 49 | 48 | 53 | 49 | **239** | ObjectBox |
| Insert: Batch | 3,938 | 9,774 | 4,647 | 220 | 3,843 | 1,488 | 221 | 219 | 4,856 | 221 | **11,943** | ObjectBox |
| Insert: Bulk | 5,056 | **14,239** | 5,190 | 220 | — | 1,311 | 221 | 280 | 4,837 | 221 | 12,170 | peewee |
| Filter: Large | 157,910 | 191,547 | 205,680 | 40,254 | 84,432 | 76,845 | 44,308 | 26,549 | 191,710 | 46,015 | **483,995** | ObjectBox |
| Filter: Small | 62,081 | 83,288 | 62,202 | 22,131 | 74,957 | 44,511 | 20,141 | 12,514 | 67,201 | 21,433 | **322,945** | ObjectBox |
| Get | 7,029 | 10,828 | 8,439 | 3,382 | 15,951 | 8,026 | 2,251 | 1,488 | 10,388 | 3,460 | **206,820** | ObjectBox |
| Filter: dict | 229,594 | **290,921** | 183,342 | 42,134 | — | 95,365 | 52,547 | 34,181 | 139,711 | 40,034 | — | peewee |
| Filter: tuple | 239,483 | 293,575 | 308,382 | 46,874 | — | 89,768 | 51,099 | 33,229 | **443,701** | 52,895 | — | SQLModel |
| Update: Whole | 6,279 | 13,575 | 11,102 | 448 | 8,667 | 3,953 | 540 | 533 | 12,139 | 449 | **32,535** | ObjectBox |
| Update: Partial | 7,013 | 18,588 | 12,133 | 447 | 9,775 | 4,122 | 540 | 535 | 13,442 | 450 | **33,414** | ObjectBox |
| Delete | 1,933 | 23,312 | 2,271 | 333 | 54 | 3,952 | 541 | 538 | 14,744 | 450 | **69,766** | ObjectBox |
| **Geometric Mean** | 11,200 | 24,559 | 13,349 | 1,862 | 4,191 | 7,586 | 2,001 | 1,655 | 16,521 | 1,951 | **35,298** | **ObjectBox** |

### Test 3: Wide Model (32+ fields)

![ObjectBox and SQLite Test 3, warm](images/sqlite_warm_test3.png)

| Operation | Django | peewee | SA ORM | SA ORM async | SQLObject | Tortoise ORM | Piccolo | ormar | SQLModel | SQLModel async | ObjectBox | Best |
|-----------|--------|--------|--------|--------------|-----------|--------------|---------|-------|----------|----------------|-----------|------|
| Insert: Single | 53 | 159 | 53 | 49 | 54 | 161 | 49 | 46 | 53 | 49 | **213** | ObjectBox |
| Insert: Batch | 2,835 | 6,156 | 4,413 | 220 | 2,965 | 1,443 | 220 | 175 | 4,344 | 219 | **10,681** | ObjectBox |
| Insert: Bulk | 4,215 | 6,229 | 4,953 | 220 | — | 1,572 | 218 | 271 | 4,345 | 219 | **11,006** | ObjectBox |
| Filter: Large | 52,574 | 48,380 | 83,627 | 16,526 | 42,335 | 33,010 | 10,545 | 9,374 | 71,886 | 11,830 | **102,493** | ObjectBox |
| Filter: Small | 26,787 | 28,309 | 40,119 | 10,184 | 38,464 | 23,917 | 8,016 | 6,091 | 35,465 | 8,754 | **91,891** | ObjectBox |
| Get | 3,876 | 3,991 | 7,757 | 2,881 | 10,636 | 6,016 | 1,667 | 1,091 | 8,537 | 2,749 | **76,018** | ObjectBox |
| Filter: dict | 62,095 | **75,773** | 66,733 | 13,238 | — | 41,920 | 13,069 | 10,373 | 52,647 | 10,976 | — | peewee |
| Filter: tuple | 67,321 | 77,127 | 94,175 | 12,335 | — | 38,029 | 12,897 | 12,415 | **99,307** | 14,831 | — | SQLModel |
| Update: Whole | 4,267 | 4,838 | 11,291 | 447 | 8,523 | 3,651 | 537 | 445 | 10,991 | 446 | **24,199** | ObjectBox |
| Update: Partial | 6,376 | 17,483 | 12,555 | 447 | 9,517 | 4,093 | 537 | 534 | 12,381 | 447 | **24,349** | ObjectBox |
| Delete | 7,072 | 22,858 | 14,053 | 447 | 54 | 4,154 | 541 | 538 | 14,029 | 447 | **71,421** | ObjectBox |
| **Geometric Mean** | 7,223 | 11,284 | 11,285 | 1,291 | 3,236 | 5,605 | 1,219 | 1,075 | 10,729 | 1,229 | **20,883** | **ObjectBox** |

---

## Analysis

### Cold: sync ORMs are faster, ObjectBox leads

On SQLite, async overhead hurts more than it helps — there is no concurrency to exploit due to SQLite's single-writer lock. Sync ORMs (peewee, SA ORM, SQLModel, Django, SQLObject) avoid the `aiosqlite` polling overhead and win handily. Among the SQL ORMs, peewee has the best geometric mean in all three tests, followed by sync SA ORM and sync SQLModel (SQLModel is ahead on Test 2, where SA ORM's model maps the relationships, which slows down its Delete). The sync variants of SA ORM and SQLModel are 2–8x faster than their async variants on reads and 13–22x on batch/bulk inserts, updates and deletes (6x for SA ORM's Delete on Test 2; single inserts, one synced commit each, are about the same). Sync SQLModel has the fastest Filter: tuple in all three tests; on the wide model (Test 3), SA ORM leads Filter: Large and Update: Whole among the SQL ORMs, and SQLObject leads Filter: Small and Get. Tortoise ORM is the fastest async ORM on SQLite.

ObjectBox (embedded object database, experimental codegen for writes and reads) has the best geometric mean in all three tests (30,568 vs peewee's 21,659, 30,001 vs 20,732 and 16,849 vs 10,218, i.e. 1.4–1.7x), though its mean leaves out Filter: dict/tuple, peewee's strongest operations. It wins every operation it runs in all three tests: Get by 4.7–10.3x over the runner-up (SQLObject), Filter: Small by 2.1–3.2x and Filter: Large by 1.3–2.4x. Single inserts (one synced commit each) are 1.3–1.5x ahead of peewee and Tortoise ORM; batch and bulk inserts, updates and deletes 1.3–3.1x ahead of the best SQL ORM. Its results are about as stable between runs as the SQL ORMs': the widest spread is Update: Whole on Test 2, where one of the five runs was ~1.7x faster than the others. These numbers are for objectbox-python branch `fast-flatbuffers-builder` @ `0ac38fa`; the previous build (`fc7c0be`), which read dates and strings a little slower, was 1–15% slower on reads and the same on writes. The 5.0.0b1 release on TestPyPI performed the same as `0ac38fa` in a quick check (geometric means within ±2%). Earlier builds imported numpy on `import objectbox`, whose idle OpenBLAS threads kept spinning while the first test operations ran and made them up to 2x slower.

### Warm: sync ORMs gain, the order stays

With a warm-up run, the sync ORMs' geometric means rise by 10–36%. The biggest gains are on batch/bulk inserts and Update: Whole (up to ~1.9x for peewee, 2x for ObjectBox's Update: Whole, 1.5x for SA ORM and SQLModel); Insert: Single, bound by one synced commit per row, doesn't change. The async ORMs stay within ±6%: they run all operations in one process anyway, so earlier operations already paid most one-time costs. ObjectBox has the best geometric mean in all three tests, as cold (36,380 / 35,298 / 20,883 vs peewee's 26,324 / 24,559 / 11,284). peewee is the fastest SQL ORM on Tests 1 and 2; on Test 3, SA ORM ties it (11,285 vs 11,284). Next come SQLModel and SA ORM (SQLModel ahead on Tests 1 and 2, on Test 1 by less than 1%). ObjectBox's lead on reads grows (Get 1.4–1.7x faster than cold, e.g. 219,081 vs 152,465 rows/sec on Test 1), while warm peewee overtakes it on Insert: Bulk in Tests 1 and 2 (14,165 vs 12,215 and 14,239 vs 12,170).

### Key takeaways

- **ObjectBox**: fastest in every operation it runs (reads 1.3–10.3x, writes 1.3–3.1x ahead of the best SQL ORM), best geometric mean (without the dict/tuple operations)
- **SQL ORMs on SQLite**: peewee and the sync variants of SA ORM and SQLModel are fastest, followed by Django; async adds overhead without any concurrency to gain
- **SA ORM async / SQLModel async** (aiosqlite): 2–8x slower than their sync variants on reads and 13–22x on batch/bulk inserts, updates and deletes. SQLModel tracks closely with SA ORM (expected — it's a thin wrapper around SQLAlchemy)
- **Tortoise ORM**: the fastest async ORM on SQLite
- **ormar**: Pydantic validation overhead causes significant slowdown, especially on wide models (Test 3)
- **SQLObject**: Missing bulk insert and dict/tuple filter operations; fast on Get and Filter: Small, but slow on Delete

## Running the benchmarks

```sh
# Clone and install
git clone https://github.com/tortoise/orm-benchmarks.git
cd orm-benchmarks
uv venv --python 3.14 && source .venv/bin/activate
# ObjectBox 5.0.0b1 is only on TestPyPI: install it first, without dependencies
uv pip install --no-deps --index-url https://test.pypi.org/simple/ objectbox==5.0.0b1 objectbox-api==5.0.0b1 objectbox-clib==5.3.2
uv pip install --no-sources -r pyproject.toml

# All ORMs and ObjectBox, Tests 1-3
cd benchmarks && sh bench.sh
# With a warm-up run before each timed operation
cd benchmarks && WARMUP=1 sh bench.sh
```

For PostgreSQL and MySQL, see [postgres-mysql.md](postgres-mysql.md).
