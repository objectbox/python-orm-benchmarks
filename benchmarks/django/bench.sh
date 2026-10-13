#!/bin/sh

cd $(dirname $0)

# WARMUP=1: run each operation once untimed before timing it (see ../warmup.py)
run() {
    if [ "${WARMUP:-0}" != 0 ]; then python ../warmup.py "$1"; else python -m "$1"; fi
}

# setup DB
../db.sh
export DJANGO_SETTINGS_MODULE="simple.settings"
./manage-simple.py migrate -v 0

# Test A → Insert
run simple.test_a

# Test B → Transactioned Intsert
run simple.test_b

# Test C → Bulk Insert
run simple.test_c

# Test D → Filter on level
run simple.test_d

# Test E → Filter limit 20
run simple.test_e

# Test F → Get
run simple.test_f

# Test G → dict
run simple.test_g

# Test H → tuple
run simple.test_h

# Test I → Update full
run simple.test_i

# Test J → Update partial
run simple.test_j

# Test K → Delete
run simple.test_k
