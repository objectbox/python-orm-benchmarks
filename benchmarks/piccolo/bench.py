#!/usr/bin/env python
import asyncio
import os
import sys

try:
    concurrents = int(os.environ.get("CONCURRENTS", "10"))

    if concurrents != 10:
        loopstr = f" C{concurrents}"
    else:
        loopstr = ""
    if os.environ.get("UVLOOP", ""):
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
finally:
    pass

import test_a
import test_b
import test_c
import test_d
import test_e
import test_f
import test_g
import test_h
import test_i
import test_j
import test_k
from models import Journal, DB

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from warmup import warm  # noqa: E402  WARMUP=1: untimed run of each operation first
from trim import trim  # noqa: E402


async def run_benchmarks():
    await DB.start_connection_pool()
    await Journal.create_table(if_not_exists=True)
    await warm(test_a.runtest, loopstr)
    await warm(test_b.runtest, loopstr)
    trim()  # untimed: delete the rows beyond ITERATIONS again (LARGE_TABLE=1 keeps them)
    await warm(test_c.runtest, loopstr)
    trim()  # untimed: delete the rows beyond ITERATIONS again (LARGE_TABLE=1 keeps them)
    await warm(test_d.runtest, loopstr)
    await warm(test_e.runtest, loopstr)
    await warm(test_f.runtest, loopstr)
    await warm(test_g.runtest, loopstr)
    await warm(test_h.runtest, loopstr)
    await warm(test_i.runtest, loopstr)
    await warm(test_j.runtest, loopstr)
    await warm(test_k.runtest, loopstr)
    await DB.close_connection_pool()


asyncio.run(run_benchmarks())
