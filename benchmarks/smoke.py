#!/usr/bin/env python
"""Smoke test: run every ORM's benchmark on SQLite with few iterations and verify the output.

A run passes when it prints one "<ORM>, <Letter>: Rows/sec: <value>" line with a positive value
for every test_<letter>.py in the ORM's directory, and nothing that looks like a traceback.

Usage: python smoke.py [-i ITERATIONS] [-t TEST ...] [ORM_DIR ...]
"""
import argparse
import os
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULT_RE = re.compile(r"^\s*(.+?),\s*([A-Z]):\s*Rows/sec:\s*([\d.]+)\s*$")


def orms_from_bench_sh():
    """ORM directories in the order bench.sh runs them."""
    orms = []
    for line in (HERE / "bench.sh").read_text().splitlines():
        m = re.match(r"^(\w+)/bench\.sh", line.strip())
        if m and m.group(1) not in orms:
            orms.append(m.group(1))
    return orms


def expected_ops(orm):
    return sorted(p.stem[-1].upper() for p in (HERE / orm).rglob("test_?.py"))


def run(orm, test, iterations):
    # bench.sh scripts call "python", so make sure it resolves to the interpreter running this
    path = os.pathsep.join([str(Path(sys.executable).parent), os.environ.get("PATH", "")])
    env = dict(os.environ, PATH=path, DBTYPE="sqlite", TEST=str(test), ITERATIONS=str(iterations))
    start = time.time()
    proc = subprocess.run(
        ["sh", str(HERE / orm / "bench.sh")],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    elapsed = time.time() - start

    got = {}
    for line in proc.stdout.splitlines():
        m = RESULT_RE.match(line)
        if m:
            got[m.group(2)] = float(m.group(3))

    problems = []
    if not expected_ops(orm):
        problems.append("no test_?.py files found")
    missing = [op for op in expected_ops(orm) if op not in got]
    if missing:
        problems.append(f"missing ops: {','.join(missing)}")
    zero = [op for op, val in got.items() if val <= 0]
    if zero:
        problems.append(f"non-positive rate: {','.join(zero)}")
    if "Traceback" in proc.stdout or "Error" in proc.stdout:
        problems.append("error output")
    return problems, elapsed, proc.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("orms", nargs="*", help="ORM directories (default: all from bench.sh)")
    parser.add_argument("-t", "--test", type=int, action="append", choices=[1, 2, 3])
    parser.add_argument("-i", "--iterations", type=int, default=100, help="must be > 20")
    parser.add_argument("-v", "--verbose", action="store_true", help="print output of failures")
    args = parser.parse_args()

    orms = args.orms or orms_from_bench_sh()
    tests = args.test or [1, 2, 3]
    print(f"Python {sys.version.split()[0]}, SQLite {sqlite3.sqlite_version}, "
          f"iterations {args.iterations}")

    failures = []
    for orm in orms:
        for test in tests:
            problems, elapsed, output = run(orm, test, args.iterations)
            status = "FAIL" if problems else "ok"
            print(f"{status:4} {orm:18} test {test}  {elapsed:6.1f}s  {'; '.join(problems)}")
            if problems:
                failures.append((orm, test, output))

    if failures and args.verbose:
        for orm, test, output in failures:
            print(f"\n----- {orm} test {test} -----\n{output.rstrip()}")

    print(f"\n{len(failures)} of {len(orms) * len(tests)} runs failed" if failures else "\nall ok")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
