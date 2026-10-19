#!/usr/bin/env python3
"""Regenerate the published SQLite results from the medians of one raw-results directory.

    tools/publish.py <results-dir>     e.g. tools/publish.py raw-results/2026-10-18

Needs <results-dir>/{sqlite,sqlite-warm,sqlite-large,sqlite-large-warm}/median/outfile{1,2,3}
(tools/median.py). Writes:
- images/{sqlite,sqlite_warm,sqlite_large,sqlite_large_warm}_{test1,test2,test3,summary}.png
- README.md: the cold/warm geometric-mean tables under "Geometric means, ..." and the six detailed
  tables (cold Tests 1-3, then warm Tests 1-3)
- large-table.md: the six detailed tables between the <!-- tables:<prefix> --> markers
The text around the tables (analysis, numbers quoted in prose) is not touched: update it by hand.
Filter: dict/tuple (G/H) are left out, as in generate_tables.py/generate_charts.py.
"""

import math
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import generate_charts as charts  # noqa: E402
import generate_tables as tables  # noqa: E402

MODES = {  # results subdirectory: image prefix
    "sqlite": "sqlite",
    "sqlite-warm": "sqlite_warm",
    "sqlite-large": "sqlite_large",
    "sqlite-large-warm": "sqlite_large_warm",
}
TABLE_TITLES = ["Test 1: Simple Model (4 fields)", "Test 2: FK Relations", "Test 3: Wide Model (32+ fields)"]
CHART_TITLES = ["Test 1: Simple Model", "Test 2: FK Relations", "Test 3: Wide Model (32+ fields)"]
GEOMEAN_ORDER = ["ObjectBox", "Django", "peewee", "SA ORM", "SA ORM async", "SQLObject", "Tortoise ORM",
                 "Piccolo", "ormar", "SQLModel", "SQLModel async"]
TABLE = re.compile(r"^\| Operation \|.*?\n\| \*\*Geometric Mean\*\* \|[^\n]*\n", re.S | re.M)


def chart_label(prefix):
    tags = [tag for tag, key in (("large table", "large"), ("warm", "warm")) if key in prefix]
    return "ObjectBox and SQLite" + (f" ({', '.join(tags)})" if tags else "")


def build_mode(median_dir, prefix):
    """Writes the charts of one mode; returns its three detailed tables and per-test geometric means."""
    label = chart_label(prefix)
    md_tables, geomeans, all_tests = [], [], []
    for i in (1, 2, 3):
        path = str(median_dir / f"outfile{i}")
        data = tables.parse_results(path)
        orms = [o for o in tables.ORM_ORDER if o in data]
        md_tables.append(tables.generate_table(data, orms) + "\n")
        geomeans.append({orm: tables.compute_geometric_mean(list(ops.values())) for orm, ops in data.items()})
        cdata = charts.parse_results(path)
        charts.generate_chart(cdata, f"{label} — {CHART_TITLES[i - 1]}", str(REPO / f"images/{prefix}_test{i}.png"))
        all_tests.append((CHART_TITLES[i - 1], cdata))
    charts.generate_geomean_summary(
        all_tests, f"{label} — Overall (Geometric Mean)", str(REPO / f"images/{prefix}_summary.png")
    )
    return md_tables, geomeans


def geomean_table(cold, warm):
    """Cold vs. warm per test; the warm column shows the ratio to cold; the best value is bold."""
    lines = ["| Database / ORM |" + "".join(f" Test {t} cold | Test {t} warm |" for t in (1, 2, 3)),
             "|-----|" + "------------:|" * 6]
    for orm in GEOMEAN_ORDER:
        if orm not in cold[0]:
            continue
        row = f"| {orm} |"
        for t in range(3):
            c, w = cold[t][orm], warm[t][orm]
            sc, sw = f"{c:,.0f}", f"{w:,.0f}"
            if c == max(cold[t].values()):
                sc = f"**{sc}**"
            if w == max(warm[t].values()):
                sw = f"**{sw}**"
            row += f" {sc} | {sw} (×{w / c:.2f}) |"
        lines.append(row)
    return "\n".join(lines)


def replace_tables(text, new_tables, where):
    old = TABLE.findall(text)
    if len(old) != len(new_tables):
        sys.exit(f"{where}: expected {len(new_tables)} detailed tables, found {len(old)}")
    parts = TABLE.split(text)
    return parts[0] + "".join(t + p for t, p in zip(new_tables, parts[1:]))


def replace_after(text, anchor, new_block):
    """Replaces the block (up to the next blank line) that follows the line `anchor`."""
    start = text.index(anchor + "\n\n") + len(anchor) + 2
    end = text.index("\n\n", start)
    return text[:start] + new_block + text[end:]


def main():
    results = Path(sys.argv[1])
    built = {mode: build_mode(results / mode / "median", prefix) for mode, prefix in MODES.items()}

    readme = (REPO / "README.md").read_text()
    readme = replace_after(readme, "Geometric means, cold vs. warm:",
                           geomean_table(built["sqlite"][1], built["sqlite-warm"][1]))
    readme = replace_after(readme, "Geometric means, large table, cold vs. warm:",
                           geomean_table(built["sqlite-large"][1], built["sqlite-large-warm"][1]))
    readme = replace_tables(readme, built["sqlite"][0] + built["sqlite-warm"][0], "README.md")
    (REPO / "README.md").write_text(readme)

    large = (REPO / "large-table.md").read_text()
    for mode in ("sqlite-large", "sqlite-large-warm"):
        marker = f"<!-- tables:{MODES[mode]} -->"
        head, rest = large.split(marker)
        section, tail = rest.split("<!-- /tables -->", 1)
        large = head + marker + replace_tables(section, built[mode][0], f"large-table.md {marker}") + "<!-- /tables -->" + tail
    (REPO / "large-table.md").write_text(large)
    print("README.md, large-table.md and images/ updated; check the numbers quoted in the text")


if __name__ == "__main__":
    main()
