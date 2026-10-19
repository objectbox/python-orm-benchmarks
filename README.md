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
| ObjectBox | **63,985** | **79,130** (×1.24) | **61,832** | **76,823** (×1.24) | **27,535** | **33,852** (×1.23) |
| Django | 17,724 | 19,674 (×1.11) | 15,328 | 16,584 (×1.08) | 8,502 | 9,019 (×1.06) |
| peewee | 32,633 | 35,901 (×1.10) | 30,257 | 33,867 (×1.12) | 13,178 | 13,862 (×1.05) |
| SA ORM | 23,111 | 28,070 (×1.21) | 17,446 | 22,426 (×1.29) | 14,017 | 16,746 (×1.19) |
| SA ORM async | 4,803 | 4,879 (×1.02) | 4,703 | 4,667 (×0.99) | 3,171 | 3,130 (×0.99) |
| SQLObject | 8,364 | 9,168 (×1.10) | 8,133 | 9,065 (×1.11) | 6,174 | 6,744 (×1.09) |
| Tortoise ORM | 14,154 | 14,266 (×1.01) | 13,949 | 14,201 (×1.02) | 8,649 | 8,905 (×1.03) |
| Piccolo | 4,119 | 4,168 (×1.01) | 4,107 | 4,028 (×0.98) | 2,290 | 2,312 (×1.01) |
| ormar | 3,166 | 3,153 (×1.00) | 3,076 | 3,021 (×0.98) | 1,550 | 1,583 (×1.02) |
| SQLModel | 23,980 | 28,290 (×1.18) | 23,553 | 27,700 (×1.18) | 13,488 | 15,794 (×1.17) |
| SQLModel async | 4,743 | 4,668 (×0.98) | 4,546 | 4,647 (×1.02) | 2,814 | 2,959 (×1.05) |

### Large table (~20,000 rows)

The same operations, but D–K run on ~20,100 rows instead of ~300: the untimed step that deletes most of the 20,000 rows that Insert: Batch and Insert: Bulk added is skipped (`LARGE_TABLE=1`). Filter: Large, dict and tuple return ~67x more rows per query, and Update: Whole, Update: Partial and Delete change all rows in one transaction, so its durable commit is spread over ~20,100 rows instead of ~300. Separate runs; detailed tables in [large-table.md](large-table.md).

![ObjectBox and SQLite Summary, large table](images/sqlite_large_summary.png)

![ObjectBox and SQLite Summary, large table, warm](images/sqlite_large_warm_summary.png)

Geometric means, large table, cold vs. warm:

| Database / ORM | Test 1 cold | Test 1 warm | Test 2 cold | Test 2 warm | Test 3 cold | Test 3 warm |
|-----|------------:|------------:|------------:|------------:|------------:|------------:|
| ObjectBox | **98,011** | **108,306** (×1.11) | **90,446** | **102,911** (×1.14) | **37,444** | **40,854** (×1.09) |
| Django | 28,753 | 29,439 (×1.02) | 23,217 | 24,057 (×1.04) | 10,745 | 10,814 (×1.01) |
| peewee | 46,220 | 47,665 (×1.03) | 42,119 | 44,440 (×1.06) | 15,582 | 15,740 (×1.01) |
| SA ORM | 51,155 | 52,901 (×1.03) | 27,508 | 29,874 (×1.09) | 22,292 | 23,396 (×1.05) |
| SA ORM async | 12,490 | 12,520 (×1.00) | 9,258 | 9,178 (×0.99) | 6,495 | 6,761 (×1.04) |
| SQLObject | 19,346 | 19,650 (×1.02) | 17,513 | 17,894 (×1.02) | 12,799 | 13,217 (×1.03) |
| Tortoise ORM | 26,043 | 27,630 (×1.06) | 19,777 | 20,570 (×1.04) | 15,375 | 14,172 (×0.92) |
| Piccolo | 9,564 | 9,567 (×1.00) | 7,855 | 7,868 (×1.00) | 4,320 | 4,334 (×1.00) |
| ormar | 6,404 | 6,473 (×1.01) | 5,685 | 5,873 (×1.03) | 2,589 | 2,636 (×1.02) |
| SQLModel | 48,900 | 50,877 (×1.04) | 47,916 | 50,326 (×1.05) | 20,603 | 21,397 (×1.04) |
| SQLModel async | 11,712 | 11,969 (×1.02) | 11,444 | 11,327 (×0.99) | 6,320 | 6,422 (×1.02) |

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
> ObjectBox is an embedded object database with its own storage engine, not an ORM on top of SQL. It uses the 5.0.0b1 beta (on TestPyPI) with its experimental FlatBuffers codegen for writes and reads enabled (`OBX_CODEGEN=0` disables it). Differences to the SQL ORMs: Test 2 uses plain indexed ids (the Python binding has no relations), Test 3 stores decimals as strings, JSON as JSON strings (like the SQL ORMs store it as text) and leaves "nullable" columns unset (no NULL support), Filter: dict/tuple are not supported (no projection API), and Update: Partial writes the whole object. Its geometric mean covers 9 operations.

### Operations

| Code | Operation | Description |
|------|-----------|-------------|
| A | Insert: Single | Insert one row at a time |
| B | Insert: Batch | Insert 10,000 rows in a single transaction, one save per row |
| C | Insert: Bulk | Insert 10,000 rows with the ORM's bulk insert API |
| D | Filter: Large | Fetch a large result set |
| E | Filter: Small | Fetch limit 20 with random offset |
| F | Get | Fetch a single row by primary key |
| G | Filter: dict | Fetch large result set as dicts |
| H | Filter: tuple | Fetch large result set as tuples |
| I | Update: Whole | Update all fields of a row |
| J | Update: Partial | Update a single field |
| K | Delete | Delete a single row |

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
| Filter: dict | 241,598 | **328,304** | 177,732 | 46,472 | — | 101,290 | 57,520 | 42,085 | 138,906 | 47,384 | — | peewee |
| Filter: tuple | 248,635 | 327,970 | 281,642 | 60,009 | — | 95,211 | 55,587 | 41,712 | **414,894** | 63,922 | — | SQLModel |
| Update: Whole | 5,552 | 8,638 | 8,807 | 649 | 6,335 | 3,414 | 540 | 452 | 8,610 | 649 | **21,330** | ObjectBox |
| Update: Partial | 5,852 | 18,607 | 9,467 | 651 | 9,512 | 3,950 | 538 | 534 | 9,417 | 648 | **60,976** | ObjectBox |
| Delete | 6,059 | 23,710 | 10,038 | 644 | 9,723 | 4,047 | 539 | 536 | 9,940 | 644 | **70,710** | ObjectBox |
| **Geometric Mean** | 17,724 | 32,633 | 23,111 | 4,803 | 8,364 | 14,154 | 4,119 | 3,166 | 23,980 | 4,743 | **63,985** | **ObjectBox** |

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
| Filter: dict | 217,295 | **285,385** | 142,523 | 49,856 | — | 99,306 | 57,239 | 39,797 | 134,178 | 45,550 | — | peewee |
| Filter: tuple | 229,909 | 292,871 | 208,440 | 61,418 | — | 93,412 | 55,623 | 38,323 | **400,271** | 61,406 | — | SQLModel |
| Update: Whole | 5,314 | 8,179 | 8,063 | 645 | 6,371 | 3,416 | 539 | 452 | 8,555 | 648 | **21,132** | ObjectBox |
| Update: Partial | 5,850 | 18,258 | 8,642 | 644 | 9,628 | 3,963 | 539 | 534 | 9,361 | 647 | **59,847** | ObjectBox |
| Delete | 2,021 | 23,182 | 2,236 | 606 | 8,969 | 3,874 | 539 | 536 | 9,999 | 644 | **67,335** | ObjectBox |
| **Geometric Mean** | 15,328 | 30,257 | 17,446 | 4,703 | 8,133 | 13,949 | 4,107 | 3,076 | 23,553 | 4,546 | **61,832** | **ObjectBox** |

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
| Filter: dict | 62,719 | **75,252** | 64,287 | 16,540 | — | 37,782 | 15,389 | 11,995 | 51,745 | 11,994 | — | peewee |
| Filter: tuple | 69,121 | 78,634 | 88,140 | 18,521 | — | 34,805 | 14,552 | 12,852 | **98,111** | 13,497 | — | SQLModel |
| Update: Whole | 3,937 | 4,068 | 8,113 | 648 | 6,232 | 2,920 | 536 | 387 | 7,950 | 646 | **15,890** | ObjectBox |
| Update: Partial | 5,455 | 17,860 | 8,892 | 647 | 9,232 | 3,879 | 535 | 452 | 8,773 | 646 | **31,468** | ObjectBox |
| Delete | 5,943 | 22,974 | 9,751 | 642 | 9,504 | 3,883 | 540 | 536 | 9,690 | 640 | **68,910** | ObjectBox |
| **Geometric Mean** | 8,502 | 13,178 | 14,017 | 3,171 | 6,174 | 8,649 | 2,290 | 1,550 | 13,488 | 2,814 | **27,535** | **ObjectBox** |

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
| Filter: dict | 266,825 | **344,605** | 199,176 | 51,976 | — | 97,180 | 59,393 | 38,567 | 149,845 | 43,565 | — | peewee |
| Filter: tuple | 274,820 | 348,625 | 335,947 | 64,961 | — | 93,052 | 56,224 | 39,370 | **475,527** | 62,997 | — | SQLModel |
| Update: Whole | 6,712 | 15,787 | 12,535 | 650 | 9,079 | 3,856 | 539 | 533 | 12,240 | 648 | **60,973** | ObjectBox |
| Update: Partial | 7,192 | 19,418 | 13,725 | 650 | 9,716 | 3,952 | 539 | 534 | 13,574 | 647 | **65,738** | ObjectBox |
| Delete | 7,490 | 24,670 | 14,720 | 645 | 9,834 | 4,038 | 539 | 536 | 14,808 | 644 | **71,174** | ObjectBox |
| **Geometric Mean** | 19,674 | 35,901 | 28,070 | 4,879 | 9,168 | 14,266 | 4,168 | 3,153 | 28,290 | 4,668 | **79,130** | **ObjectBox** |

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
| Filter: dict | 238,837 | **309,307** | 198,063 | 49,522 | — | 97,114 | 57,435 | 39,456 | 146,901 | 45,277 | — | peewee |
| Filter: tuple | 255,019 | 307,703 | 326,786 | 55,993 | — | 91,621 | 55,477 | 36,397 | **462,013** | 53,325 | — | SQLModel |
| Update: Whole | 6,439 | 14,253 | 11,261 | 646 | 9,035 | 3,824 | 538 | 452 | 12,369 | 648 | **61,255** | ObjectBox |
| Update: Partial | 7,150 | 19,044 | 12,278 | 645 | 9,755 | 3,986 | 539 | 534 | 13,685 | 648 | **64,840** | ObjectBox |
| Delete | 2,011 | 23,909 | 2,477 | 594 | 9,049 | 3,874 | 540 | 536 | 14,763 | 644 | **68,849** | ObjectBox |
| **Geometric Mean** | 16,584 | 33,867 | 22,426 | 4,667 | 9,065 | 14,201 | 4,028 | 3,021 | 27,700 | 4,647 | **76,823** | **ObjectBox** |

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
| Filter: dict | 64,555 | **77,931** | 72,511 | 16,248 | — | 38,863 | 15,081 | 12,548 | 54,757 | 13,364 | — | peewee |
| Filter: tuple | 69,960 | 80,827 | 101,691 | 16,199 | — | 35,623 | 14,240 | 11,990 | **104,108** | 17,396 | — | SQLModel |
| Update: Whole | 4,423 | 5,049 | 11,385 | 648 | 8,793 | 3,524 | 535 | 445 | 11,174 | 646 | **36,597** | ObjectBox |
| Update: Partial | 6,485 | 18,298 | 12,453 | 648 | 9,509 | 3,963 | 536 | 532 | 12,395 | 646 | **38,641** | ObjectBox |
| Delete | 7,293 | 23,703 | 14,208 | 643 | 9,609 | 4,039 | 539 | 536 | 14,172 | 642 | **71,018** | ObjectBox |
| **Geometric Mean** | 9,019 | 13,862 | 16,746 | 3,130 | 6,744 | 8,905 | 2,312 | 1,583 | 15,794 | 2,959 | **33,852** | **ObjectBox** |

---

## Analysis

### Cold: ObjectBox about 2x the best SQL ORM

ObjectBox (embedded object database, experimental codegen for writes and reads) has the best geometric mean in all three tests, about 2x the best SQL ORM (63,985 vs peewee's 32,633, 61,832 vs peewee's 30,257 and 27,535 vs SA ORM's 14,017), though its mean leaves out Filter: dict/tuple, peewee's and SQLModel's strongest operations. It is fastest in every operation it runs: Get by 4.7–9.9x over the runner-up (SQLObject), Filter: Small by 2.3–3.1x, Filter: Large by 1.3–2.4x; Insert: Batch by 2.5–4.0x, Insert: Bulk by 1.2–1.8x, updates and deletes by 1.8–3.3x; Insert: Single (one synced commit each) by 1.3–1.5x over peewee and Tortoise ORM.

Among the SQL ORMs, peewee has the best geometric mean on Tests 1 and 2; on the wide model (Test 3), SA ORM (14,017) and SQLModel (13,488) are ahead of peewee (13,178). With 10,000 objects per transaction, the insert paths differ much more than with 100: SA ORM and SQLModel insert a batch at ~46,000 rows/sec on Test 1 (peewee ~26,000, Django ~16,000), and each SQL ORM's bulk insert is 2–5x faster than its batch insert (ObjectBox: 1.1–1.3x; its batch insert is already faster than any SQL ORM's bulk insert).

On SQLite, async adds overhead without any concurrency to gain (one writer at a time). The sync variants of SA ORM and SQLModel are 2–7x faster than their async variants on reads, 2.5–7x on batch/bulk inserts and 12–16x on updates and deletes (SA ORM's Delete on Test 2: 3.7x); single inserts, one synced commit each, are about the same. Tortoise ORM is the fastest async ORM, close to Django. Sync SQLModel has the fastest Filter: tuple and peewee the fastest Filter: dict in all three tests.

Insert: Bulk returns the new IDs only for Django, Piccolo and ObjectBox (see [Operations](#operations)); the others' bulk paths leave the objects without IDs.

### Warm: sync ORMs and ObjectBox gain, the order stays

With a warm-up run, the sync ORMs' geometric means rise by 5–29% (SA ORM and SQLModel most), ObjectBox's by 23–24%; the async ORMs stay within ±5%: they run all operations in one process anyway, so earlier operations already paid most one-time costs. Insert: Single, bound by one synced commit per row, doesn't change. ObjectBox has the best geometric mean in all three tests, 2.0–2.3x the best SQL ORM (79,130 / 76,823 / 33,852 vs peewee's 35,901 / 33,867 and SA ORM's 16,746 on Test 3). Its biggest gains are Update: Whole (2.3–2.9x faster than cold) and Get (1.4–1.7x).

### Large table: the commit is amortized, ObjectBox stays ahead

With ~20,100 rows, updates and deletes spread their one durable commit over 67x more rows, so most ORMs' geometric means rise 1.2–2.6x; ObjectBox again has the best one in all three tests, 1.7–1.9x the best SQL ORM cold (98,011 vs SA ORM's 51,155, 90,446 vs SQLModel's 47,916, 37,444 vs SA ORM's 22,292) and 1.7–2.1x warm. Among the SQL ORMs, SA ORM leads on Tests 1 and 3 and SQLModel on Test 2 (where SA ORM's Delete holds it back); peewee follows. Among the SQL ORMs, SQLObject has the fastest updates; on Test 3 it edges out ObjectBox on Update: Partial (57,789 vs 56,683 rows/sec). peewee is ~10% faster than ObjectBox on Filter: Small on Test 1 (122,009 vs 110,913) and on par on Test 2: ObjectBox's limit/offset query gets slower with ~4,000 instead of ~60 matching rows per level (266k rows/sec on the default table), while SQLite's index scan stops after the offset and 20 rows. Django has the fastest Filter: dict on Tests 1 and 2, and SQLModel passes a million rows/sec on Filter: tuple.

Delete on Test 2 (FK relations) is the slowest operation on the large table for SA ORM (1,143 rows/sec), SA ORM async (1,272), Piccolo (1,434), Tortoise ORM (1,522), ormar (2,169) and Django (2,424), while peewee, SQLModel and SQLObject delete 44,000–102,000 rows/sec. SA ORM and Tortoise ORM get 2.0x and 2.5x slower per row than on ~300 rows (2,236 and 3,874); the likely cause is per-row lookups of related rows (children through the self-reference, M2M links) that grow with the table: in the SA ORM model, the self-referencing `parent_id` has no index.

One more effect of the larger batches: the rows deleted after Insert: Batch and Insert: Bulk leave free space in the database files, so later writes mostly don't grow the files. For ObjectBox this makes update commits cheaper (fdatasync of the data file ~1.7 ms instead of ~6.2 ms when the file grows), so on Test 1 its Update: Whole and Update: Partial are 1.3x and 1.9x faster than with 100-object batches. A database that has been in use for a while is usually in this state too.

### Key takeaways

- **ObjectBox**: 1.7–2.3x the best SQL ORM's geometric mean (cold, warm and large table; without the dict/tuple operations); fastest in every operation it runs except, on the large table, Filter: Small on Test 1 (peewee) and Update: Partial on Test 3 (SQLObject, 2% ahead)
- **Batch sizes matter**: with 100 objects per transaction, batch and bulk inserts mostly measure one durable commit (~8 ms); with 10,000, the SQL ORMs' bulk inserts are 2–5x faster than their batch inserts, and the sync SQL ORMs' batch inserts differ up to 3x
- **SQL ORMs on SQLite**: peewee and the sync variants of SA ORM and SQLModel are fastest (peewee on the simple models, SA ORM and SQLModel on the wide model and the large table), followed by Django; async adds overhead without any concurrency to gain
- **SA ORM async / SQLModel async** (aiosqlite): 2–7x slower than their sync variants on reads, 2.5–7x on batch/bulk inserts and 12–16x on updates and deletes. SQLModel tracks closely with SA ORM (expected — it's a thin wrapper around SQLAlchemy)
- **Bulk insert and IDs**: only Django, Piccolo and ObjectBox set the new IDs on bulk-inserted objects
- **Tortoise ORM**: the fastest async ORM on SQLite
- **ormar**: Pydantic validation overhead causes significant slowdown, especially on wide models (Test 3)
- **SQLObject**: no bulk insert and no dict/tuple filters; fast on Get, and the fastest SQL ORM on updates on the large table

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
