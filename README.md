# Python Embedded Database Benchmarks: ObjectBox and SQLite

Performance benchmarks of embedded databases in Python: the object database [ObjectBox](https://github.com/objectbox/objectbox-python) and SQLite, accessed through popular Python ORMs. Everything runs in-process on local storage, without a database server.

Older results for PostgreSQL and MySQL (SQL ORMs only, earlier benchmark version, different machine) are in [postgres-mysql.md](postgres-mysql.md).

Higher is better: rows (objects) per second, as the geometric mean over the 9 object operations of each test (SQLObject has no bulk insert, so its mean covers 8; see [Setup](#setup)). Each value is the median of 5 full runs.

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
| ObjectBox | **63,985** | **79,130** (×1.24) | **61,832** | **76,823** (×1.24) | **27,535** | **33,852** (×1.23) |
| Django | 9,887 | 10,986 (×1.11) | 8,450 | 9,101 (×1.08) | 5,395 | 5,772 (×1.07) |
| peewee | 19,539 | 21,691 (×1.11) | 18,323 | 20,728 (×1.13) | 8,904 | 9,407 (×1.06) |
| SA ORM | 13,955 | 17,136 (×1.23) | 10,486 | 13,072 (×1.25) | 9,648 | 11,645 (×1.21) |
| SA ORM async | 2,819 | 2,813 (×1.00) | 2,719 | 2,724 (×1.00) | 2,170 | 2,171 (×1.00) |
| SQLObject | 8,364 | 9,168 (×1.10) | 8,133 | 9,065 (×1.11) | 6,174 | 6,744 (×1.09) |
| Tortoise ORM | 9,203 | 9,359 (×1.02) | 9,080 | 9,324 (×1.03) | 6,290 | 6,481 (×1.03) |
| Piccolo | 2,302 | 2,324 (×1.01) | 2,294 | 2,240 (×0.98) | 1,509 | 1,534 (×1.02) |
| ormar | 1,783 | 1,804 (×1.01) | 1,748 | 1,722 (×0.99) | 976 | 1,004 (×1.03) |
| SQLModel | 14,372 | 17,180 (×1.20) | 14,170 | 16,834 (×1.19) | 9,318 | 11,156 (×1.20) |
| SQLModel async | 2,751 | 2,728 (×0.99) | 2,635 | 2,752 (×1.04) | 2,013 | 2,056 (×1.02) |

### Large table (~20,000 rows)

The same operations, but D–K run on ~20,100 rows instead of ~300: the untimed step that deletes most of the 20,000 rows that Insert: Batch and Insert: Bulk added is skipped (`LARGE_TABLE=1`). Filter: Large returns ~67x more rows per query, and Update: Whole, Update: Partial and Delete change all rows in one transaction, so its durable commit is spread over ~20,100 rows instead of ~300. Separate runs; detailed tables in [large-table.md](large-table.md).

![ObjectBox and SQLite Summary, large table](images/sqlite_large_summary.png)

![ObjectBox and SQLite Summary, large table, warm](images/sqlite_large_warm_summary.png)

Geometric means, large table, cold vs. warm:

| Database / ORM | Test 1 cold | Test 1 warm | Test 2 cold | Test 2 warm | Test 3 cold | Test 3 warm |
|-----|------------:|------------:|------------:|------------:|------------:|------------:|
| ObjectBox | **98,011** | **108,306** (×1.11) | **90,446** | **102,911** (×1.14) | **37,444** | **40,854** (×1.09) |
| Django | 14,215 | 14,610 (×1.03) | 11,044 | 11,444 (×1.04) | 6,770 | 6,826 (×1.01) |
| peewee | 26,396 | 27,487 (×1.04) | 24,323 | 25,777 (×1.06) | 10,556 | 10,698 (×1.01) |
| SA ORM | 30,336 | 31,570 (×1.04) | 14,433 | 15,863 (×1.10) | 16,556 | 17,525 (×1.06) |
| SA ORM async | 8,211 | 8,311 (×1.01) | 5,861 | 5,917 (×1.01) | 5,468 | 5,641 (×1.03) |
| SQLObject | 19,346 | 19,650 (×1.02) | 17,513 | 17,894 (×1.02) | 12,799 | 13,217 (×1.03) |
| Tortoise ORM | 18,188 | 19,637 (×1.08) | 12,974 | 13,627 (×1.05) | 12,289 | 11,396 (×0.93) |
| Piccolo | 5,802 | 5,795 (×1.00) | 4,565 | 4,581 (×1.00) | 3,249 | 3,272 (×1.01) |
| ormar | 3,802 | 3,845 (×1.01) | 3,366 | 3,439 (×1.02) | 1,809 | 1,842 (×1.02) |
| SQLModel | 29,435 | 30,833 (×1.05) | 28,911 | 30,608 (×1.06) | 15,634 | 16,378 (×1.05) |
| SQLModel async | 7,807 | 8,006 (×1.03) | 7,745 | 7,761 (×1.00) | 5,364 | 5,540 (×1.03) |

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

> **Environment:** Python 3.14.6, SQLite 3.53.1 (bundled with uv's CPython build), Linux x86_64 (AMD Ryzen 9 5950X, ext4 on NVMe), 100 iterations per operation (Insert: Batch and Insert: Bulk: 10,000 objects), CPU frequency governor `performance`, 1-minute load average below 1 before each ORM run. Each value is the median of 5 full runs (2026-10-18/19; warm peewee and Tortoise ORM: 5 runs of their own on 2026-10-19 after a fix to the warm-up restore; see [raw results](raw-results/2026-10-18/), which also lists the changes since the previous results). SQLite runs with `synchronous=FULL` (its compiled-in default), so every committed transaction is synced to disk, as with ObjectBox.
>
> ObjectBox is an embedded object database with its own storage engine, not an ORM on top of SQL. It uses the 5.0.0b1 beta (on TestPyPI) with its experimental FlatBuffers codegen for writes and reads enabled (`OBX_CODEGEN=0` disables it). Differences to the SQL ORMs: Test 2 uses plain indexed ids (the Python binding has no relations), Test 3 stores decimals as strings, JSON as JSON strings (like the SQL ORMs store it as text) and leaves "nullable" columns unset (no NULL support), and Update: Partial writes the whole object.

### Operations

| Code | Operation | Description |
|------|-----------|-------------|
| A | Insert: Single | Insert one row at a time |
| B | Insert: Batch | Insert 10,000 rows in a single transaction, one save per row |
| C | Insert: Bulk | Insert 10,000 rows with the ORM's bulk insert API |
| D | Filter: Large | Fetch a large result set |
| E | Filter: Small | Fetch limit 20 with random offset |
| F | Get | Fetch a single row by primary key |
| I | Update: Whole | Update all fields of a row |
| J | Update: Partial | Update a single field |
| K | Delete | Delete a single row |

The suite also measures fetching a large result set as dicts (G) and as tuples (H) for the SQL ORMs; these aren't object operations, so they're left out of the tables, charts and geometric means (the raw results contain them). ObjectBox has no projection API for them.

Only persisting is timed: the insert operations create the unsaved objects before the timer starts, and the update operations choose the new values before it, so creating objects (including field defaults) and generating test data don't count. SQLObject inserts the row when it creates the object, so for SQLObject only the field values are prepared; peewee's bulk insert prepares row tuples and applies defaults while inserting. Right before the timer starts, each test runs `gc.collect()` and `gc.freeze()`, so garbage from the preparation isn't collected while timed.

B and C insert 10,000 objects (`BATCH_SIZE`); the other operations run 100 iterations. A durable commit costs ~8 ms here, so with 100 objects per transaction (the setting before 2026-10-18) B and C mostly measured that one commit, not the inserts. After B and after C, an untimed step deletes the newest 9,900 rows again, so D–K run on ~300 rows. The [large-table results](#large-table-20000-rows) skip that step (`LARGE_TABLE=1`): D–K run on ~20,100 rows.

Insert: Bulk uses each ORM's fastest bulk path. Only Django (`bulk_create()`), Piccolo (`insert()`) and ObjectBox (`put()` of a list) set the new IDs on the inserted objects. SA ORM and SQLModel, sync and async (`bulk_save_objects()`), Tortoise ORM and ormar (`bulk_create()`) and peewee (`insert_many()` of row tuples) don't: to use the IDs, the objects have to be read back. In SA ORM and SQLModel, `session.add_all()` does set the IDs, but it inserts row by row, like Insert: Batch. Piccolo and ormar split the insert into chunks within one transaction, as SQLite allows at most 32,766 variables per statement.

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
| Insert: Single | 54 | 160 | 53 | 49 | 54 | 160 | 49 | 46 | 53 | 49 | **246** | ObjectBox |
| Insert: Batch | 15,700 | 26,062 | 45,780 | 9,991 | 14,632 | 19,923 | 5,260 | 3,321 | 46,264 | 9,133 | **186,830** | ObjectBox |
| Insert: Bulk | 79,499 | 101,765 | 124,122 | 21,006 | — | 80,086 | 17,739 | 16,821 | 127,314 | 17,152 | **225,900** | ObjectBox |
| Filter: Large | 172,185 | 230,507 | 190,512 | 46,331 | 83,199 | 82,249 | 47,441 | 27,313 | 181,031 | 49,166 | **461,065** | ObjectBox |
| Filter: Small | 53,981 | 90,522 | 50,015 | 22,991 | 39,829 | 49,027 | 21,496 | 12,788 | 57,535 | 24,262 | **265,819** | ObjectBox |
| Get | 7,354 | 12,305 | 8,319 | 3,756 | 15,592 | 8,426 | 2,499 | 1,561 | 9,905 | 3,673 | **153,835** | ObjectBox |
| Update: Whole | 5,552 | 8,638 | 8,807 | 649 | 6,335 | 3,414 | 540 | 452 | 8,610 | 649 | **21,330** | ObjectBox |
| Update: Partial | 5,852 | 18,607 | 9,467 | 651 | 9,512 | 3,950 | 538 | 534 | 9,417 | 648 | **60,976** | ObjectBox |
| Delete | 6,059 | 23,710 | 10,038 | 644 | 9,723 | 4,047 | 539 | 536 | 9,940 | 644 | **70,710** | ObjectBox |
| **Geometric Mean** | 9,887 | 19,539 | 13,955 | 2,819 | 8,364 | 9,203 | 2,302 | 1,783 | 14,372 | 2,751 | **63,985** | **ObjectBox** |

### Test 2: FK Relations

![ObjectBox and SQLite Test 2](images/sqlite_test2.png)

| Operation | Django | peewee | SA ORM | SA ORM async | SQLObject | Tortoise ORM | Piccolo | ormar | SQLModel | SQLModel async | ObjectBox | Best |
|-----------|--------|--------|--------|--------------|-----------|--------------|---------|-------|----------|----------------|-----------|------|
| Insert: Single | 54 | 160 | 53 | 49 | 54 | 160 | 49 | 48 | 53 | 49 | **235** | ObjectBox |
| Insert: Batch | 14,523 | 25,078 | 30,330 | 9,016 | 13,796 | 19,849 | 4,985 | 3,308 | 44,909 | 9,090 | **174,948** | ObjectBox |
| Insert: Bulk | 71,208 | 98,542 | 124,462 | 20,371 | — | 78,639 | 20,585 | 14,127 | 124,009 | 17,109 | **226,388** | ObjectBox |
| Filter: Large | 156,486 | 193,262 | 156,160 | 44,995 | 78,488 | 79,984 | 45,139 | 28,486 | 179,520 | 41,869 | **454,273** | ObjectBox |
| Filter: Small | 57,393 | 79,682 | 43,669 | 22,416 | 39,688 | 48,582 | 20,769 | 12,112 | 55,997 | 20,114 | **246,231** | ObjectBox |
| Get | 6,999 | 11,066 | 7,218 | 3,589 | 14,980 | 8,233 | 2,368 | 1,538 | 9,650 | 3,570 | **148,893** | ObjectBox |
| Update: Whole | 5,314 | 8,179 | 8,063 | 645 | 6,371 | 3,416 | 539 | 452 | 8,555 | 648 | **21,132** | ObjectBox |
| Update: Partial | 5,850 | 18,258 | 8,642 | 644 | 9,628 | 3,963 | 539 | 534 | 9,361 | 647 | **59,847** | ObjectBox |
| Delete | 2,021 | 23,182 | 2,236 | 606 | 8,969 | 3,874 | 539 | 536 | 9,999 | 644 | **67,335** | ObjectBox |
| **Geometric Mean** | 8,450 | 18,323 | 10,486 | 2,719 | 8,133 | 9,080 | 2,294 | 1,748 | 14,170 | 2,635 | **61,832** | **ObjectBox** |

### Test 3: Wide Model (32+ fields)

![ObjectBox and SQLite Test 3](images/sqlite_test3.png)

| Operation | Django | peewee | SA ORM | SA ORM async | SQLObject | Tortoise ORM | Piccolo | ormar | SQLModel | SQLModel async | ObjectBox | Best |
|-----------|--------|--------|--------|--------------|-----------|--------------|---------|-------|----------|----------------|-----------|------|
| Insert: Single | 53 | 159 | 53 | 49 | 54 | 159 | 48 | 46 | 53 | 48 | **210** | ObjectBox |
| Insert: Batch | 6,030 | 9,657 | 23,230 | 8,376 | 6,681 | 15,061 | 3,480 | 1,022 | 20,292 | 7,773 | **57,326** | ObjectBox |
| Insert: Bulk | 17,878 | 24,721 | 53,386 | 21,232 | — | 38,744 | 9,322 | 3,006 | 43,601 | 15,835 | **65,741** | ObjectBox |
| Filter: Large | 51,929 | 49,379 | 75,525 | 15,586 | 41,581 | 31,226 | 11,509 | 8,783 | 68,446 | 12,845 | **97,091** | ObjectBox |
| Filter: Small | 25,542 | 27,156 | 29,650 | 9,843 | 26,075 | 22,567 | 8,398 | 6,142 | 31,842 | 9,509 | **73,252** | ObjectBox |
| Get | 3,974 | 4,141 | 6,993 | 2,990 | 9,947 | 5,357 | 1,726 | 1,126 | 7,649 | 2,815 | **46,872** | ObjectBox |
| Update: Whole | 3,937 | 4,068 | 8,113 | 648 | 6,232 | 2,920 | 536 | 387 | 7,950 | 646 | **15,890** | ObjectBox |
| Update: Partial | 5,455 | 17,860 | 8,892 | 647 | 9,232 | 3,879 | 535 | 452 | 8,773 | 646 | **31,468** | ObjectBox |
| Delete | 5,943 | 22,974 | 9,751 | 642 | 9,504 | 3,883 | 540 | 536 | 9,690 | 640 | **68,910** | ObjectBox |
| **Geometric Mean** | 5,395 | 8,904 | 9,648 | 2,170 | 6,174 | 6,290 | 1,509 | 976 | 9,318 | 2,013 | **27,535** | **ObjectBox** |

## Detailed results: warm

In the cold results, each sync ORM runs every operation in a fresh process, so the timed loop also pays one-time costs such as opening a lazily opened connection, compiling the first statements, filling the ORM's caches and, for ObjectBox, compiling its codegen (imports are never timed). These runs use the warm-up mode (`WARMUP=1`): each operation first runs once untimed in the same process (async ORMs: the same event loop), the database is restored to its state before that run (rows and ID sequences), and then the operation runs again and is timed. Same machine, versions and settings as the cold results; each value is the median of 5 full runs.

### Test 1: Simple Model (4 fields)

![ObjectBox and SQLite Test 1, warm](images/sqlite_warm_test1.png)

| Operation | Django | peewee | SA ORM | SA ORM async | SQLObject | Tortoise ORM | Piccolo | ormar | SQLModel | SQLModel async | ObjectBox | Best |
|-----------|--------|--------|--------|--------------|-----------|--------------|---------|-------|----------|----------------|-----------|------|
| Insert: Single | 54 | 161 | 54 | 49 | 54 | 160 | 49 | 47 | 54 | 49 | **245** | ObjectBox |
| Insert: Batch | 16,483 | 26,045 | 46,837 | 9,114 | 14,525 | 20,690 | 5,360 | 3,326 | 48,892 | 9,162 | **199,003** | ObjectBox |
| Insert: Bulk | 81,830 | 121,472 | 142,979 | 20,938 | — | 89,231 | 17,824 | 15,050 | 132,777 | 16,947 | **248,341** | ObjectBox |
| Filter: Large | 185,561 | 240,095 | 216,134 | 50,272 | 88,463 | 79,936 | 49,818 | 28,321 | 205,529 | 46,168 | **500,454** | ObjectBox |
| Filter: Small | 61,224 | 90,879 | 71,652 | 23,096 | 48,363 | 45,732 | 21,533 | 12,637 | 68,305 | 23,960 | **322,597** | ObjectBox |
| Get | 7,809 | 12,621 | 9,055 | 3,759 | 17,170 | 8,278 | 2,493 | 1,568 | 10,863 | 3,702 | **218,056** | ObjectBox |
| Update: Whole | 6,712 | 15,787 | 12,535 | 650 | 9,079 | 3,856 | 539 | 533 | 12,240 | 648 | **60,973** | ObjectBox |
| Update: Partial | 7,192 | 19,418 | 13,725 | 650 | 9,716 | 3,952 | 539 | 534 | 13,574 | 647 | **65,738** | ObjectBox |
| Delete | 7,490 | 24,670 | 14,720 | 645 | 9,834 | 4,038 | 539 | 536 | 14,808 | 644 | **71,174** | ObjectBox |
| **Geometric Mean** | 10,986 | 21,691 | 17,136 | 2,813 | 9,168 | 9,359 | 2,324 | 1,804 | 17,180 | 2,728 | **79,130** | **ObjectBox** |

### Test 2: FK Relations

![ObjectBox and SQLite Test 2, warm](images/sqlite_warm_test2.png)

| Operation | Django | peewee | SA ORM | SA ORM async | SQLObject | Tortoise ORM | Piccolo | ormar | SQLModel | SQLModel async | ObjectBox | Best |
|-----------|--------|--------|--------|--------------|-----------|--------------|---------|-------|----------|----------------|-----------|------|
| Insert: Single | 54 | 161 | 53 | 49 | 54 | 161 | 49 | 46 | 54 | 49 | **238** | ObjectBox |
| Insert: Batch | 14,795 | 26,393 | 31,444 | 9,168 | 13,646 | 20,524 | 4,985 | 3,308 | 45,413 | 9,126 | **179,491** | ObjectBox |
| Insert: Bulk | 73,159 | 119,021 | 144,639 | 20,442 | — | 86,345 | 17,115 | 12,694 | 127,065 | 20,231 | **234,197** | ObjectBox |
| Filter: Large | 168,837 | 202,751 | 211,613 | 46,175 | 86,462 | 79,001 | 46,219 | 28,793 | 197,596 | 48,154 | **489,132** | ObjectBox |
| Filter: Small | 63,013 | 89,639 | 72,104 | 21,997 | 53,383 | 49,204 | 19,783 | 12,033 | 65,521 | 21,334 | **322,790** | ObjectBox |
| Get | 7,409 | 11,842 | 8,767 | 3,601 | 16,777 | 8,141 | 2,362 | 1,525 | 10,840 | 3,614 | **216,146** | ObjectBox |
| Update: Whole | 6,439 | 14,253 | 11,261 | 646 | 9,035 | 3,824 | 538 | 452 | 12,369 | 648 | **61,255** | ObjectBox |
| Update: Partial | 7,150 | 19,044 | 12,278 | 645 | 9,755 | 3,986 | 539 | 534 | 13,685 | 648 | **64,840** | ObjectBox |
| Delete | 2,011 | 23,909 | 2,477 | 594 | 9,049 | 3,874 | 540 | 536 | 14,763 | 644 | **68,849** | ObjectBox |
| **Geometric Mean** | 9,101 | 20,728 | 13,072 | 2,724 | 9,065 | 9,324 | 2,240 | 1,722 | 16,834 | 2,752 | **76,823** | **ObjectBox** |

### Test 3: Wide Model (32+ fields)

![ObjectBox and SQLite Test 3, warm](images/sqlite_warm_test3.png)

| Operation | Django | peewee | SA ORM | SA ORM async | SQLObject | Tortoise ORM | Piccolo | ormar | SQLModel | SQLModel async | ObjectBox | Best |
|-----------|--------|--------|--------|--------------|-----------|--------------|---------|-------|----------|----------------|-----------|------|
| Insert: Single | 54 | 160 | 53 | 49 | 54 | 159 | 49 | 47 | 54 | 49 | **211** | ObjectBox |
| Insert: Batch | 6,016 | 9,858 | 23,557 | 8,120 | 6,696 | 15,056 | 3,608 | 1,069 | 20,863 | 7,772 | **57,141** | ObjectBox |
| Insert: Bulk | 18,362 | 26,589 | 55,627 | 17,525 | — | 40,691 | 9,589 | 2,979 | 44,933 | 16,160 | **65,411** | ObjectBox |
| Filter: Large | 53,704 | 50,369 | 85,741 | 17,147 | 44,112 | 31,579 | 11,740 | 8,548 | 77,616 | 13,810 | **102,670** | ObjectBox |
| Filter: Small | 26,840 | 29,558 | 41,605 | 11,267 | 30,812 | 21,733 | 8,889 | 5,838 | 39,789 | 10,035 | **89,600** | ObjectBox |
| Get | 3,983 | 4,225 | 7,835 | 2,965 | 10,888 | 5,340 | 1,736 | 1,104 | 8,804 | 2,891 | **80,120** | ObjectBox |
| Update: Whole | 4,423 | 5,049 | 11,385 | 648 | 8,793 | 3,524 | 535 | 445 | 11,174 | 646 | **36,597** | ObjectBox |
| Update: Partial | 6,485 | 18,298 | 12,453 | 648 | 9,509 | 3,963 | 536 | 532 | 12,395 | 646 | **38,641** | ObjectBox |
| Delete | 7,293 | 23,703 | 14,208 | 643 | 9,609 | 4,039 | 539 | 536 | 14,172 | 642 | **71,018** | ObjectBox |
| **Geometric Mean** | 5,772 | 9,407 | 11,645 | 2,171 | 6,744 | 6,481 | 1,534 | 1,004 | 11,156 | 2,056 | **33,852** | **ObjectBox** |

---

## Analysis

### Cold: ObjectBox about 3x the best SQL ORM

ObjectBox (embedded object database, experimental codegen for writes and reads) has the best geometric mean in all three tests, 2.9–3.4x the best SQL ORM (63,985 vs peewee's 19,539, 61,832 vs peewee's 18,323 and 27,535 vs SA ORM's 9,648). It is fastest in every operation: Get by 4.7–9.9x over the runner-up (SQLObject), Filter: Small by 2.3–3.1x, Filter: Large by 1.3–2.4x; Insert: Batch by 2.5–4.0x, Insert: Bulk by 1.2–1.8x, updates and deletes by 1.8–3.3x; Insert: Single (one synced commit each) by 1.3–1.5x over peewee and Tortoise ORM.

Among the SQL ORMs, peewee has the best geometric mean on Tests 1 and 2, followed by SQLModel and SA ORM; on the wide model (Test 3), SA ORM (9,648) and SQLModel (9,318) are ahead of peewee (8,904). peewee and Tortoise ORM run SQLite in WAL mode, the others with SQLite's default rollback journal: with one durable commit per row, Insert: Single is ~3x faster in WAL mode (160 vs 46–54 rows/sec), so their write results include that advantage. With 10,000 objects per transaction, the insert paths differ much more than with 100: SA ORM and SQLModel insert a batch at ~46,000 rows/sec on Test 1 (peewee ~26,000, Django ~16,000), and each SQL ORM's bulk insert is 2–5x faster than its batch insert (ObjectBox: 1.1–1.3x; its batch insert is already faster than any SQL ORM's bulk insert).

On SQLite, async adds overhead without any concurrency to gain (one writer at a time). The sync variants of SA ORM and SQLModel are 2–5x faster than their async variants on reads, 2.5–7x on batch/bulk inserts and 12–16x on updates and deletes (SA ORM's Delete on Test 2: 3.7x); single inserts, one synced commit each, are about the same. Tortoise ORM is the fastest async ORM, on par with Django (ahead on Tests 2 and 3).

Insert: Bulk returns the new IDs only for Django, Piccolo and ObjectBox (see [Operations](#operations)); the others' bulk paths leave the objects without IDs.

### Warm: sync ORMs and ObjectBox gain, the order stays

With a warm-up run, the sync ORMs' geometric means rise by 6–25% (SA ORM and SQLModel most), ObjectBox's by 23–24%; the async ORMs stay within ±4%: they run all operations in one process anyway, so earlier operations already paid most one-time costs. Insert: Single, bound by one synced commit per row, doesn't change. ObjectBox has the best geometric mean in all three tests, 2.9–3.7x the best SQL ORM (79,130 / 76,823 / 33,852 vs peewee's 21,691 / 20,728 and SA ORM's 11,645 on Test 3). Its biggest gains are Update: Whole (2.3–2.9x faster than cold) and Get (1.4–1.7x).

### Large table: the commit is amortized, ObjectBox stays ahead

With ~20,100 rows, updates and deletes spread their one durable commit over 67x more rows, so the geometric means rise 1.1–2.9x; ObjectBox again has the best one in all three tests, 2.3–3.2x the best SQL ORM cold (98,011 vs SA ORM's 30,336, 90,446 vs SQLModel's 28,911, 37,444 vs SA ORM's 16,556) and 2.3–3.4x warm. Among the SQL ORMs, SA ORM leads on Tests 1 and 3 and SQLModel on Test 2 (where SA ORM's Delete holds it back); peewee follows. Among the SQL ORMs, SQLObject has the fastest updates; on Test 3 it edges out ObjectBox on Update: Partial (57,789 vs 56,683 rows/sec). peewee is ~10% faster than ObjectBox on Filter: Small on Test 1 (122,009 vs 110,913) and on par on Test 2: ObjectBox's limit/offset query gets slower with ~4,000 instead of ~60 matching rows per level (266k rows/sec on the default table), while SQLite's index scan stops after the offset and 20 rows.

Delete on Test 2 (FK relations) is the slowest operation on the large table for SA ORM (1,143 rows/sec), SA ORM async (1,272), Piccolo (1,434), Tortoise ORM (1,522), ormar (2,169) and Django (2,424), while peewee, SQLModel and SQLObject delete 44,000–102,000 rows/sec. SA ORM and Tortoise ORM get 2.0x and 2.5x slower per row than on ~300 rows (2,236 and 3,874); the likely cause is per-row lookups of related rows (children through the self-reference, M2M links) that grow with the table: in the SA ORM model, the self-referencing `parent_id` has no index.

One more effect of the larger batches: the rows deleted after Insert: Batch and Insert: Bulk leave free space in the database files, so later writes mostly don't grow the files. For ObjectBox this makes update commits cheaper (fdatasync of the data file ~1.7 ms instead of ~6.2 ms when the file grows), so on Test 1 its Update: Whole and Update: Partial are 1.3x and 1.9x faster than with 100-object batches. A database that has been in use for a while is usually in this state too.

### Key takeaways

- **ObjectBox**: 2.3–3.7x the best SQL ORM's geometric mean (cold, warm and large table); fastest in every operation it runs except, on the large table, Filter: Small on Test 1 (peewee) and Update: Partial on Test 3 (SQLObject, 2% ahead)
- **Batch sizes matter**: with 100 objects per transaction, batch and bulk inserts mostly measure one durable commit (~8 ms); with 10,000, the SQL ORMs' bulk inserts are 2–5x faster than their batch inserts, and the sync SQL ORMs' batch inserts differ up to 3x
- **SQL ORMs on SQLite**: peewee and the sync variants of SA ORM and SQLModel are fastest (peewee on the simple models, SA ORM and SQLModel on the wide model and the large table), followed by Django; async adds overhead without any concurrency to gain
- **SA ORM async / SQLModel async** (aiosqlite): 2–5x slower than their sync variants on reads, 2.5–7x on batch/bulk inserts and 12–16x on updates and deletes. SQLModel tracks closely with SA ORM (expected — it's a thin wrapper around SQLAlchemy)
- **Bulk insert and IDs**: only Django, Piccolo and ObjectBox set the new IDs on bulk-inserted objects
- **Tortoise ORM**: the fastest async ORM on SQLite
- **ormar**: Pydantic validation overhead causes significant slowdown, especially on wide models (Test 3)
- **SQLObject**: no bulk insert; fast on Get, and the fastest SQL ORM on updates on the large table

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
