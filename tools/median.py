#!/usr/bin/env python3
"""Median of the runs of one mode, and the run-to-run spread.

    tools/median.py <mode-dir>     e.g. tools/median.py raw-results/2026-10-18/sqlite

Reads <mode-dir>/run<n>/outfile{1,2,3}, writes <mode-dir>/median/outfile{1,2,3} (the median per ORM
and operation, in first-seen order) and prints the widest spreads (max/min across runs). Lines a rerun
appended to an outfile count like any other: drop the replaced lines first (see AGENTS.md).
"""

import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

LINE = re.compile(r"^\s*(.+?),\s*([A-K]):\s*Rows/sec:\s*([\d.]+)")


def main():
    mode_dir = Path(sys.argv[1])
    runs = sorted(d for d in mode_dir.glob("run*") if d.name[3:].isdigit())
    if not runs:
        sys.exit(f"no run<n> directories in {mode_dir}")
    out = mode_dir / "median"
    out.mkdir(exist_ok=True)
    for t in (1, 2, 3):
        vals = defaultdict(list)
        for run in runs:
            for line in (run / f"outfile{t}").read_text().splitlines():
                m = LINE.match(line)
                if m:
                    vals[m.group(1).strip(), m.group(2)].append(float(m.group(3)))
        with open(out / f"outfile{t}", "w") as f:
            for (orm, op), v in vals.items():
                f.write(f"{orm}, {op}: Rows/sec: {statistics.median(v):10.2f}\n")
        print(f"Test {t}: widest spread (max/min) across {len(runs)} runs")
        spread = sorted(((max(v) / min(v), k, len(v)) for k, v in vals.items()), reverse=True)
        for s, (orm, op), n in spread[:8]:
            print(f"  {orm:14} {op}  {s:5.2f}x  n={n}")


if __name__ == "__main__":
    main()
