# ORM Benchmarks

Comprehensive performance benchmarks comparing popular Python ORMs across PostgreSQL, MySQL, and SQLite.

**Tested ORMs:**

| ORM | Type | PostgreSQL | MySQL | SQLite |
|-----|------|:---:|:---:|:---:|
| [Tortoise ORM](https://github.com/tortoise/tortoise-orm) | async | asyncpg | asyncmy | aiosqlite |
| [Django](https://www.djangoproject.com/) | sync | psycopg2 | mysqlclient | sqlite3 |
| [peewee](https://github.com/coleifer/peewee) | sync | psycopg2 | pymysql | sqlite3 |
| [SQLAlchemy ORM](http://www.sqlalchemy.org/) | sync | psycopg2 | mysqlclient | sqlite3 |
| [SQLAlchemy ORM (async)](http://www.sqlalchemy.org/) | async | asyncpg | aiomysql | aiosqlite |
| [SQLObject](https://github.com/sqlobject/sqlobject) | sync | psycopg2 | mysqlclient | sqlite3 |
| [Piccolo](https://github.com/piccolo-orm/piccolo) | async | asyncpg | — | aiosqlite |
| [ormar](https://github.com/collerek/ormar) | async | asyncpg | aiomysql | aiosqlite |
| [SQLModel](https://github.com/tiangolo/sqlmodel) | sync | psycopg2 | mysqlclient | sqlite3 |
| [SQLModel (async)](https://github.com/tiangolo/sqlmodel) | async | asyncpg | aiomysql | aiosqlite |
| [ObjectBox](https://github.com/objectbox/objectbox-python) | sync | — | — | embedded (own storage engine) |

> **Environment:** Python 3.14, macOS (Apple Silicon), 100 iterations per operation.
> Piccolo does not support MySQL.
> Sync SQLAlchemy ("SA ORM") and sync SQLModel are only in the SQLite results so far; the PostgreSQL/MySQL runs predate them, and their "SQLModel" chart labels refer to SQLModel async.
> ObjectBox is an embedded object database, not an ORM on top of SQL, so it is only compared in the SQLite runs. It uses the unreleased 5.0.0b1 beta with its experimental FlatBuffers codegen for writes and reads enabled (`OBX_CODEGEN=0` disables it). Differences to the SQL ORMs: Test 2 uses plain indexed ids (the Python binding has no relations), Test 3 stores decimals as strings, JSON as JSON strings (like the SQL ORMs store it as text) and leaves "nullable" columns unset (no NULL support), Filter: dict/tuple are not supported (no projection API), and Update: Partial writes the whole object. Its geometric mean covers 9 operations.

## Operations

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

## Test Models

**Test 1 — Simple model** (4 fields): `id`, `timestamp`, `level` (indexed), `text` (indexed)

**Test 2 — FK relations**: Same as Test 1, plus self-referential foreign key, reverse FK, and M2M relation

**Test 3 — Wide model** (32+ fields): Same as Test 1, plus 4 sets of 8 typed columns (float, smallint, int, bigint, char, text, decimal, json) — 2 with defaults, 2 nullable

---

## Results: PostgreSQL 17

PostgreSQL 17 in Docker. Driver: `asyncpg` for async ORMs, `psycopg2` for sync ORMs.

### Overview

![PostgreSQL Summary](images/pg_summary.png)

### Test 1: Simple Model (4 fields)

![PostgreSQL Test 1](images/pg_test1.png)

| Operation | Django | peewee | SA ORM async | SQLObject | Tortoise ORM | Piccolo | ormar | SQLModel async | Best |
|-----------|--------|--------|--------------|-----------|--------------|---------|-------|----------|------|
| Insert: Single | 776 | 651 | 584 | 699 | **3,455** | 3,240 | 283 | 540 | Tortoise ORM |
| Insert: Batch | 2,069 | 2,418 | 1,154 | 1,575 | **14,033** | 12,138 | 1,048 | 1,081 | Tortoise ORM |
| Insert: Bulk | 5,224 | 5,009 | 1,264 | — | **18,807** | 18,060 | 1,178 | 1,079 | Tortoise ORM |
| Filter: Large | 57,451 | 62,009 | 32,318 | 50,694 | 143,810 | **147,031** | 19,735 | 32,389 | Piccolo |
| Filter: Small | 19,491 | 18,066 | 7,532 | 24,844 | **60,699** | 45,805 | 5,501 | 6,444 | Tortoise ORM |
| Get | 2,183 | 2,590 | 1,894 | 3,341 | 6,420 | **6,854** | 846 | 1,792 | Piccolo |
| Filter: dict | 64,394 | 81,652 | 33,798 | — | 209,380 | **328,124** | 26,777 | 31,117 | Piccolo |
| Filter: tuple | 55,080 | 66,827 | 37,933 | — | 197,175 | **332,310** | 23,286 | 34,411 | Piccolo |
| Update: Whole | 2,896 | 3,555 | 1,743 | 1,995 | **17,407** | 13,491 | 2,538 | 1,781 | Tortoise ORM |
| Update: Partial | 3,281 | 4,812 | 1,526 | 3,802 | **18,255** | 16,180 | 2,740 | 1,856 | Tortoise ORM |
| Delete | 3,386 | 5,701 | 1,869 | 843 | **21,010** | 18,968 | 2,890 | 1,895 | Tortoise ORM |
| **Geometric Mean** | 7,108 | 8,257 | 3,816 | 3,622 | 29,381 | **29,514** | 3,233 | 3,660 | **Piccolo** |

### Test 2: FK Relations

![PostgreSQL Test 2](images/pg_test2.png)

| Operation | Django | peewee | SA ORM async | SQLObject | Tortoise ORM | Piccolo | ormar | SQLModel async | Best |
|-----------|--------|--------|--------------|-----------|--------------|---------|-------|----------|------|
| Insert: Single | 765 | 822 | 564 | 517 | **3,350** | 3,075 | 264 | 521 | Tortoise ORM |
| Insert: Batch | 2,654 | 2,477 | 1,184 | 1,140 | **12,355** | 8,785 | 1,067 | 1,061 | Tortoise ORM |
| Insert: Bulk | 4,733 | 5,863 | 1,146 | — | **21,969** | 12,461 | 1,157 | 1,120 | Tortoise ORM |
| Filter: Large | 59,181 | 58,026 | 32,641 | 47,745 | **137,275** | 115,754 | 14,400 | 32,614 | Tortoise ORM |
| Filter: Small | 16,460 | 19,514 | 6,792 | 29,200 | 47,951 | **50,408** | 4,899 | 8,051 | Piccolo |
| Get | 2,394 | 2,605 | 1,905 | 1,440 | **5,870** | 5,665 | 787 | 1,922 | Tortoise ORM |
| Filter: dict | 73,174 | 78,313 | 33,632 | — | 207,239 | **303,737** | 25,848 | 31,831 | Piccolo |
| Filter: tuple | 65,459 | 70,256 | 34,130 | — | 192,246 | **284,733** | 29,597 | 36,273 | Piccolo |
| Update: Whole | 3,216 | 3,791 | 1,598 | 1,907 | **16,647** | 12,217 | 2,400 | 1,665 | Tortoise ORM |
| Update: Partial | 3,392 | 4,586 | 1,729 | 4,022 | **18,796** | 15,065 | 2,442 | 1,781 | Tortoise ORM |
| Delete | 866 | 5,880 | 896 | 629 | **17,921** | 12,984 | 2,940 | 1,711 | Tortoise ORM |
| **Geometric Mean** | 6,587 | 8,631 | 3,484 | 2,949 | **27,860** | 24,918 | 3,082 | 3,710 | **Tortoise ORM** |

### Test 3: Wide Model (32+ fields)

![PostgreSQL Test 3](images/pg_test3.png)

| Operation | Django | peewee | SA ORM async | SQLObject | Tortoise ORM | Piccolo | ormar | SQLModel async | Best |
|-----------|--------|--------|--------------|-----------|--------------|---------|-------|----------|------|
| Insert: Single | 660 | 712 | 555 | 683 | 1,560 | **2,761** | 177 | 507 | Piccolo |
| Insert: Batch | 1,580 | 1,338 | 1,137 | 1,280 | **8,077** | 4,627 | 542 | 953 | Tortoise ORM |
| Insert: Bulk | 3,374 | 3,074 | 1,187 | — | **9,571** | 5,596 | 814 | 971 | Tortoise ORM |
| Filter: Large | 32,188 | 25,686 | 26,031 | 26,710 | **50,995** | 29,431 | 2,893 | 23,445 | Tortoise ORM |
| Filter: Small | 8,946 | 9,546 | 7,167 | 20,497 | **31,247** | 18,652 | 2,105 | 5,997 | Tortoise ORM |
| Get | 1,541 | 1,311 | 1,773 | 2,288 | **5,056** | 3,563 | 626 | 1,708 | Tortoise ORM |
| Filter: dict | 28,900 | 32,299 | 22,351 | — | 71,887 | **121,813** | 6,883 | 22,634 | Piccolo |
| Filter: tuple | 34,619 | 30,980 | 29,794 | — | 66,990 | **121,798** | 6,353 | 29,111 | Piccolo |
| Update: Whole | 2,067 | 1,386 | 1,620 | 2,150 | **12,590** | 5,181 | 1,375 | 1,559 | Tortoise ORM |
| Update: Partial | 3,113 | 3,960 | 1,689 | 3,873 | **19,986** | 5,512 | 59 | 1,680 | Tortoise ORM |
| Delete | 3,480 | 4,915 | 1,728 | 769 | **22,214** | 14,305 | 2,595 | 1,574 | Tortoise ORM |
| **Geometric Mean** | 4,851 | 4,712 | 3,432 | 3,025 | **16,587** | 12,145 | 1,097 | 3,152 | **Tortoise ORM** |

---

## Results: MySQL 8

MySQL 8 in Docker. Driver: `asyncmy` for Tortoise, `aiomysql` for SA async / ormar, `mysqlclient` for Django, `pymysql` for peewee / SQLObject. Piccolo does not support MySQL.

### Overview

![MySQL Summary](images/mysql_summary.png)

### Test 1: Simple Model (4 fields)

![MySQL Test 1](images/mysql_test1.png)

| Operation | Django | peewee | SA ORM async | SQLObject | Tortoise ORM | ormar | SQLModel async | Best |
|-----------|--------|--------|--------------|-----------|--------------|-------|----------|------|
| Insert: Single | 460 | 475 | 1,260 | 386 | **2,226** | 1,218 | 1,198 | Tortoise ORM |
| Insert: Batch | 1,685 | 3,403 | 4,425 | 1,743 | **10,352** | 3,903 | 3,639 | Tortoise ORM |
| Insert: Bulk | 2,888 | 8,244 | 4,704 | — | **13,545** | 5,669 | 3,614 | Tortoise ORM |
| Filter: Large | 53,093 | 57,706 | 70,552 | 49,274 | **98,361** | 29,059 | 62,415 | Tortoise ORM |
| Filter: Small | 13,216 | 19,768 | 31,251 | 23,637 | **52,596** | 16,702 | 33,064 | Tortoise ORM |
| Get | 2,058 | 2,065 | 4,486 | 3,340 | **6,891** | 1,753 | 4,132 | Tortoise ORM |
| Filter: dict | 65,185 | 64,735 | 77,599 | — | **126,411** | 67,878 | 65,702 | Tortoise ORM |
| Filter: tuple | 62,068 | 57,817 | 101,337 | — | **124,069** | 69,064 | 99,444 | Tortoise ORM |
| Update: Whole | 2,422 | 3,203 | 2,376 | 2,211 | **12,485** | 5,086 | 2,152 | Tortoise ORM |
| Update: Partial | 3,568 | 4,624 | 2,510 | 6,088 | **14,040** | 6,045 | 2,439 | Tortoise ORM |
| Delete | 3,421 | 4,937 | 2,574 | 406 | **13,740** | 8,243 | 2,515 | Tortoise ORM |
| **Geometric Mean** | 6,035 | 8,000 | 8,998 | 3,307 | **21,351** | 8,885 | 8,221 | **Tortoise ORM** |

### Test 2: FK Relations

![MySQL Test 2](images/mysql_test2.png)

| Operation | Django | peewee | SA ORM async | SQLObject | Tortoise ORM | ormar | SQLModel async | Best |
|-----------|--------|--------|--------------|-----------|--------------|-------|----------|------|
| Insert: Single | 477 | 525 | 1,173 | 399 | **1,777** | 952 | 1,063 | Tortoise ORM |
| Insert: Batch | 2,458 | 3,374 | 4,873 | 1,825 | **8,299** | 3,278 | 3,853 | Tortoise ORM |
| Insert: Bulk | 4,029 | **12,401** | 3,807 | — | 7,852 | 5,261 | 3,452 | peewee |
| Filter: Large | 60,201 | 50,582 | 71,476 | 46,076 | **95,298** | 21,057 | 69,532 | Tortoise ORM |
| Filter: Small | 13,404 | 14,109 | 26,652 | 21,838 | **58,097** | 8,354 | 31,293 | Tortoise ORM |
| Get | 2,146 | 2,171 | 3,965 | 3,227 | **7,188** | 1,719 | 4,333 | Tortoise ORM |
| Filter: dict | 70,525 | 63,725 | 70,878 | — | **122,091** | 48,115 | 54,117 | Tortoise ORM |
| Filter: tuple | 59,955 | 42,729 | 102,362 | — | **120,419** | 41,905 | 103,458 | Tortoise ORM |
| Update: Whole | 2,443 | 3,229 | 2,026 | 2,140 | **7,588** | 4,045 | 2,187 | Tortoise ORM |
| Update: Partial | 3,774 | 3,953 | 2,183 | 4,642 | **11,806** | 5,555 | 2,565 | Tortoise ORM |
| Delete | 917 | 5,191 | 883 | 328 | **12,982** | 5,491 | 2,461 | Tortoise ORM |
| **Geometric Mean** | 5,883 | 7,759 | 7,567 | 3,061 | **18,337** | 6,707 | 8,134 | **Tortoise ORM** |

### Test 3: Wide Model (32+ fields)

![MySQL Test 3](images/mysql_test3.png)

| Operation | Django | peewee | SA ORM async | SQLObject | Tortoise ORM | ormar | SQLModel async | Best |
|-----------|--------|--------|--------------|-----------|--------------|-------|----------|------|
| Insert: Single | 368 | 366 | 1,318 | 342 | **1,331** | 703 | 1,071 | Tortoise ORM |
| Insert: Batch | 1,583 | 2,076 | 4,225 | 1,372 | **4,384** | 860 | 2,405 | Tortoise ORM |
| Insert: Bulk | 2,623 | 3,506 | 3,403 | — | **6,167** | 2,290 | 2,400 | Tortoise ORM |
| Filter: Large | 30,557 | 16,564 | 27,000 | 30,339 | **35,672** | 3,393 | 22,934 | Tortoise ORM |
| Filter: Small | 8,812 | 6,830 | 14,421 | 16,180 | **23,723** | 2,765 | 14,136 | Tortoise ORM |
| Get | 1,616 | 1,017 | 2,270 | 2,656 | **4,014** | 839 | 2,187 | Tortoise ORM |
| Filter: dict | 30,032 | 18,525 | 22,793 | — | **48,723** | 7,504 | 22,733 | Tortoise ORM |
| Filter: tuple | 35,392 | 21,983 | 31,740 | — | **41,779** | 7,659 | 29,487 | Tortoise ORM |
| Update: Whole | 1,852 | 1,590 | 1,456 | 2,207 | **8,684** | 1,715 | 1,410 | Tortoise ORM |
| Update: Partial | 3,407 | 4,148 | 1,512 | 5,091 | **13,981** | 5,052 | 1,517 | Tortoise ORM |
| Delete | 3,166 | 4,352 | 1,559 | 401 | **16,320** | 7,646 | 1,450 | Tortoise ORM |
| **Geometric Mean** | 4,466 | 3,943 | 4,928 | 2,692 | **11,560** | 2,629 | 4,292 | **Tortoise ORM** |

---

## Results: SQLite

SQLite on local filesystem (`/tmp/db.sqlite3`). This benchmark is inherently single-threaded due to SQLite's write lock — async ORMs pay overhead without concurrency benefit.

> **Environment (SQLite results only):** Python 3.14.6, SQLite 3.53.1 (bundled with uv's CPython build), Linux x86_64 (AMD Ryzen 9 5950X, ext4 on NVMe), 100 iterations per operation, 1-minute load average below 1 before each ORM run. Each value is the median of 5 full runs. These numbers come from a different machine than the PostgreSQL/MySQL results, so don't compare them across sections. SQLite runs with `synchronous=FULL` (its compiled-in default), so every committed transaction is synced to disk, as with ObjectBox.

### Overview

![SQLite Summary](images/sqlite_summary.png)

### Test 1: Simple Model (4 fields)

![SQLite Test 1](images/sqlite_test1.png)

| Operation | Django | peewee | SA ORM | SA ORM async | SQLObject | Tortoise ORM | Piccolo | ormar | SQLModel | SQLModel async | ObjectBox | Best |
|-----------|--------|--------|--------|--------------|-----------|--------------|---------|-------|----------|----------------|-----------|------|
| Insert: Single | 53 | 158 | 52 | 49 | 53 | 157 | 49 | 46 | 51 | 47 | **239** | ObjectBox |
| Insert: Batch | 2,772 | 5,825 | 3,098 | 218 | 2,750 | 1,378 | 180 | 217 | 2,400 | 210 | **8,014** | ObjectBox |
| Insert: Bulk | 3,326 | 7,367 | 3,370 | 219 | — | 1,519 | 220 | 278 | 2,411 | 211 | **10,394** | ObjectBox |
| Filter: Large | 168,124 | **223,398** | 184,779 | 36,637 | 81,378 | 49,837 | 41,350 | 21,943 | 178,603 | 32,064 | 215,306 | peewee |
| Filter: Small | 57,232 | 84,363 | 54,789 | 19,226 | 67,073 | 46,862 | 17,673 | 12,486 | 54,030 | 17,518 | **141,318** | ObjectBox |
| Get | 7,217 | 12,060 | 8,395 | 3,537 | 14,983 | 8,655 | 2,396 | 1,495 | 9,616 | 3,158 | **68,900** | ObjectBox |
| Filter: dict | 240,416 | **317,831** | 171,952 | 43,073 | — | 96,732 | 52,798 | 32,928 | 136,220 | 38,019 | — | peewee |
| Filter: tuple | 248,679 | 316,902 | 275,307 | 45,648 | — | 90,995 | 51,600 | 35,123 | **386,026** | 48,002 | — | SQLModel |
| Update: Whole | 5,480 | 8,567 | 8,658 | 384 | 6,218 | 3,242 | 536 | 448 | 8,239 | 384 | **15,724** | ObjectBox |
| Update: Partial | 5,801 | 13,429 | 9,410 | 384 | 9,320 | 3,693 | 536 | 448 | 8,956 | 384 | **30,269** | ObjectBox |
| Delete | 6,050 | 15,681 | 10,010 | 385 | 53 | 3,827 | 539 | 452 | 9,611 | 388 | **63,098** | ObjectBox |
| **Geometric Mean** | 11,318 | 20,582 | 13,001 | 1,800 | 3,721 | 7,194 | 1,937 | 1,546 | 12,360 | 1,718 | **22,092** | **ObjectBox** |

### Test 2: FK Relations

![SQLite Test 2](images/sqlite_test2.png)

| Operation | Django | peewee | SA ORM | SA ORM async | SQLObject | Tortoise ORM | Piccolo | ormar | SQLModel | SQLModel async | ObjectBox | Best |
|-----------|--------|--------|--------|--------------|-----------|--------------|---------|-------|----------|----------------|-----------|------|
| Insert: Single | 53 | 157 | 52 | 47 | 53 | 157 | 49 | 47 | 52 | 47 | **231** | ObjectBox |
| Insert: Batch | 2,701 | 5,756 | 2,741 | 216 | 2,703 | 1,362 | 180 | 216 | 2,350 | 207 | **7,498** | ObjectBox |
| Insert: Bulk | 3,283 | 7,392 | 2,978 | 217 | — | 1,520 | 218 | 397 | 2,378 | 210 | **9,715** | ObjectBox |
| Filter: Large | 157,143 | 196,017 | 149,434 | 31,279 | 78,336 | 49,446 | 38,075 | 19,964 | 168,302 | 26,665 | **207,817** | ObjectBox |
| Filter: Small | 50,730 | 82,186 | 41,612 | 17,365 | 66,118 | 44,013 | 18,150 | 11,223 | 49,403 | 15,023 | **131,230** | ObjectBox |
| Get | 6,868 | 10,950 | 6,928 | 3,136 | 14,730 | 9,254 | 2,339 | 1,382 | 9,157 | 3,046 | **66,318** | ObjectBox |
| Filter: dict | 215,771 | **291,237** | 140,742 | 41,473 | — | 107,600 | 54,752 | 32,073 | 129,800 | 37,116 | — | peewee |
| Filter: tuple | 223,660 | 290,551 | 204,086 | 44,436 | — | 99,757 | 50,484 | 32,249 | **383,977** | 46,358 | — | SQLModel |
| Update: Whole | 5,328 | 8,096 | 7,919 | 382 | 6,214 | 3,367 | 455 | 390 | 8,093 | 385 | **15,674** | ObjectBox |
| Update: Partial | 5,789 | 13,200 | 8,573 | 383 | 9,531 | 3,798 | 455 | 448 | 11,573 | 384 | **30,200** | ObjectBox |
| Delete | 2,003 | 15,664 | 2,163 | 293 | 53 | 3,735 | 456 | 451 | 9,928 | 385 | **60,834** | ObjectBox |
| **Geometric Mean** | 9,757 | 19,634 | 9,768 | 1,679 | 3,686 | 7,344 | 1,839 | 1,522 | 12,353 | 1,648 | **21,231** | **ObjectBox** |

### Test 3: Wide Model (32+ fields)

![SQLite Test 3](images/sqlite_test3.png)

| Operation | Django | peewee | SA ORM | SA ORM async | SQLObject | Tortoise ORM | Piccolo | ormar | SQLModel | SQLModel async | ObjectBox | Best |
|-----------|--------|--------|--------|--------------|-----------|--------------|---------|-------|----------|----------------|-----------|------|
| Insert: Single | 52 | 155 | 53 | 49 | 53 | 155 | 48 | 44 | 51 | 48 | **203** | ObjectBox |
| Insert: Batch | 2,139 | 4,270 | 2,842 | 216 | 2,209 | 1,157 | 179 | 146 | 1,884 | 199 | **4,540** | ObjectBox |
| Insert: Bulk | 2,820 | **4,344** | 3,135 | 217 | — | 1,321 | 213 | 258 | 1,913 | 202 | 4,254 | peewee |
| Filter: Large | 51,379 | 48,347 | **74,935** | 9,642 | 41,141 | 23,165 | 9,109 | 6,545 | 65,962 | 9,243 | 60,274 | SA ORM |
| Filter: Small | 23,787 | 26,582 | 31,058 | 7,568 | 36,644 | 21,260 | 7,274 | 5,126 | 31,863 | 7,465 | **38,353** | ObjectBox |
| Get | 3,839 | 4,115 | 6,690 | 2,327 | 9,681 | 4,905 | 1,694 | 1,030 | 7,516 | 2,579 | **22,198** | ObjectBox |
| Filter: dict | 61,394 | **75,234** | 62,682 | 11,453 | — | 35,142 | 13,020 | 8,723 | 50,228 | 9,532 | — | peewee |
| Filter: tuple | 66,704 | 78,157 | 86,057 | 12,424 | — | 32,615 | 12,584 | 10,257 | **96,384** | 10,777 | — | SQLModel |
| Update: Whole | 3,834 | 3,975 | 8,121 | 384 | 6,119 | 3,111 | 394 | 383 | 7,943 | 383 | **12,323** | ObjectBox |
| Update: Partial | 5,337 | 12,805 | 8,859 | 381 | 9,058 | 3,569 | 451 | 449 | 8,665 | 382 | **13,844** | ObjectBox |
| Delete | 5,863 | 15,659 | 9,788 | 381 | 53 | 3,669 | 537 | 452 | 9,715 | 380 | **49,045** | ObjectBox |
| **Geometric Mean** | 6,392 | 9,695 | 8,899 | 1,107 | 2,899 | 4,733 | 1,113 | 919 | 8,067 | 1,063 | **10,596** | **ObjectBox** |

---

## Analysis

### PostgreSQL — Async ORMs dominate

Tortoise ORM and Piccolo share the top spots. Both use `asyncpg`, which provides binary protocol encoding and connection pooling — a massive advantage over `psycopg2`-based sync ORMs. Piccolo leads on simple reads (Filter: dict/tuple) thanks to its ultra-thin result mapping layer, while Tortoise excels at writes (Insert, Update, Delete) and wins overall on the more complex Test 2 and Test 3 schemas.

### MySQL — Tortoise ORM leads decisively

Tortoise ORM wins every test by a wide margin (2x over the runner-up). The `asyncmy` driver (native async MySQL protocol) outperforms both `aiomysql` and sync `mysqlclient`/`pymysql`. SA ORM async is competitive on reads but falls behind on writes. Piccolo does not support MySQL.

### SQLite — Sync ORMs are faster

On SQLite, async overhead hurts more than it helps — there is no concurrency to exploit due to SQLite's single-writer lock. Sync ORMs (peewee, SA ORM, SQLModel, Django, SQLObject) avoid the `aiosqlite` polling overhead and win handily. Among the SQL ORMs, peewee has the best geometric mean in all three tests, followed by sync SA ORM and sync SQLModel (SQLModel is ahead on Test 2, where SA ORM's model maps the relationships, which slows down its Delete). The sync variants of SA ORM and SQLModel are 2–9x faster than their async variants on reads and 7–26x on batch/bulk inserts, updates and deletes (single inserts, one synced commit each, are about the same). Sync SQLModel has the fastest Filter: tuple in all three tests; on the wide model (Test 3), SA ORM leads Filter: Large and Update: Whole among the SQL ORMs, and SQLObject leads Filter: Small and Get. Tortoise ORM remains the fastest async ORM on SQLite.

ObjectBox (embedded object database, experimental codegen for writes and reads) has the best geometric mean in all three tests (22,092 vs peewee's 20,582, 21,231 vs 19,634 and 10,596 vs 9,695), though its mean leaves out Filter: dict/tuple, peewee's strongest operations. It wins Get in all three tests by 2.3–4.6x over the runner-up and Filter: Small by 1.05–1.7x. Filter: Large is close to peewee on Test 1 (215k vs 223k rows/sec), ahead on Test 2, and behind SA ORM on Test 3 (60k vs 75k). It wins every write operation except Insert: Bulk on Test 3, where peewee is 2% ahead. ObjectBox's write results vary between runs much more than the SQL ORMs': individual runs are either at a typical level or 2–4x slower (e.g. Delete on Test 1: 22,658 in one run, 61,000–64,000 in the other four), while peewee's and SA ORM's mostly stayed within a few percent. The medians reflect the typical level.

### Key takeaways

- **For PostgreSQL/MySQL production workloads**: Tortoise ORM and Piccolo (PG only) offer the best throughput
- **For SQLite/local development**: peewee and the sync variants of SA ORM and SQLModel are fastest, followed by Django; async adds overhead without any concurrency to gain
- **SA ORM async / SQLModel async**: Strong on reads but consistently slow on writes due to Session/UoW overhead (on SQLite, their sync variants don't share this write penalty). SQLModel tracks closely with SA ORM (expected — it's a thin wrapper around SQLAlchemy)
- **ormar**: Pydantic validation overhead causes significant slowdown, especially on wide models (Test 3)
- **SQLObject**: Missing bulk insert and dict/tuple filter operations, but surprisingly fast on single-row SQLite operations
- **ObjectBox** (SQLite runs only): fastest Get and small filters, wins nearly all writes, best geometric mean (without the dict/tuple operations)

## Running the benchmarks

```sh
# Clone and install
git clone https://github.com/tortoise/orm-benchmarks.git
cd orm-benchmarks
uv venv && source .venv/bin/activate
uv pip install -e .

# SQLite (default)
cd benchmarks && sh bench.sh

# PostgreSQL
export DBTYPE=postgres PASSWORD=yourpassword PGPORT=5432
cd benchmarks && sh bench.sh

# MySQL
export DBTYPE=mysql PASSWORD=yourpassword MYPORT=3306
cd benchmarks && sh bench.sh
```
