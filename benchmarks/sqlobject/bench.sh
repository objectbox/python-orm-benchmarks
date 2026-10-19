#!/bin/sh

cd $(dirname $0)

# WARMUP=1: run each operation once untimed before timing it (see ../warmup.py)
run() {
    if [ "${WARMUP:-0}" != 0 ]; then python ../warmup.py "$1"; else python -m "$1"; fi
}

# setup DB
../db.sh
python -m set_up

# Test A → Insert
run test_a

# Test B → Transactioned Intsert
run test_b
python ../trim.py  # untimed: delete the rows beyond ITERATIONS again (LARGE_TABLE=1 keeps them)

# Test C → Bulk Insert
# Not available

# Test D → Filter on level
run test_d

# Test E → Filter limit 20
run test_e

# Test F → Get
run test_f

# Test I → Update full
run test_i

# Test I → Update full
run test_j

# Test K → Delete
run test_k
