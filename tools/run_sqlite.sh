#!/bin/bash
# Full SQLite runs for publishing: each mode x run x test x ORM, all ORMs in bench.sh order.
#
#   tools/run_sqlite.sh <out-dir>     e.g. tools/run_sqlite.sh raw-results/2026-10-18
#
# Writes <out-dir>/<mode>/run<n>/outfile<test> (the raw-results layout) and logs one line per
# ORM x test to stdout. Before each ORM x test it waits until the 1-minute load average is below 1;
# one ORM x test is stopped after 1 h. Check the log: "rows" is the number of Rows/sec lines
# (11 per SQL ORM, SQLObject 8, ObjectBox 9); "non-result lines" are warnings or errors.
#
# Env: MODES (default: sqlite sqlite-warm sqlite-large sqlite-large-warm), RUNS (default: 1 2 3 4 5),
# ORMS (default: all ORMs in bench.sh; set it to rerun some, e.g. ORMS="peewee tortoise"),
# ITERATIONS (default 100), BATCH_SIZE (default 10000).
# Modes: sqlite = cold, *-warm = WARMUP=1, *-large* = LARGE_TABLE=1.
set -u
[ $# = 1 ] || { echo "usage: $0 <out-dir>" >&2; exit 2; }
OUT_BASE=$(realpath -m "$1")
cd "$(dirname "$0")/../benchmarks" || exit 1
export DBTYPE=sqlite ITERATIONS=${ITERATIONS:-100} BATCH_SIZE=${BATCH_SIZE:-10000}
ORMS=${ORMS:-$(grep -oE '^[a-z_]+/bench\.sh' bench.sh | cut -d/ -f1 | awk '!s[$0]++')}
echo "$(python -V), SQLite $(python -c 'import sqlite3; print(sqlite3.sqlite_version)'), ITERATIONS $ITERATIONS, BATCH_SIZE $BATCH_SIZE"
echo "ORMs:" $ORMS
for mode in ${MODES:-sqlite sqlite-warm sqlite-large sqlite-large-warm}; do
  case $mode in *warm*) export WARMUP=1;; *) export WARMUP=0;; esac
  case $mode in *large*) export LARGE_TABLE=1;; *) export LARGE_TABLE=0;; esac
  for r in ${RUNS:-1 2 3 4 5}; do
    dir=$OUT_BASE/$mode/run$r
    mkdir -p "$dir"
    for t in 1 2 3; do
      export TEST=$t
      : > "$dir/outfile$t"
      for orm in $ORMS; do
        waited=0
        while (( $(awk '{print ($1 < 1.0)}' /proc/loadavg) == 0 )); do sleep 5; waited=$((waited + 5)); done
        start=$(date +%s)
        log=$(timeout 3600 sh "$orm/bench.sh" 2>&1); rc=$?
        printf '%s\n' "$log" >> "$dir/outfile$t"
        rows=$(printf '%s\n' "$log" | grep -c 'Rows/sec')
        other=$(printf '%s\n' "$log" | grep -vc 'Rows/sec')
        echo "$(date +%H:%M) [$mode run $r test $t] $orm: waited ${waited}s, took $(( $(date +%s) - start ))s, rows $rows$([ "$other" != 0 ] && echo ", non-result lines $other")$([ $rc = 124 ] && echo ', TIMEOUT')"
      done
    done
  done
done
echo DONE
