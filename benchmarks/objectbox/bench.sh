#!/bin/sh

cd $(dirname $0)

# ObjectBox is an embedded database, so it only runs alongside the SQLite benchmarks
if [ "$DBTYPE" = "postgres" ] || [ "$DBTYPE" = "mysql" ]
then
    exit 0
fi

# setup DB
python -m set_up

# Test A → Insert
python -m test_a

# Test B → Transactioned Intsert
python -m test_b

# Test C → Bulk Insert
python -m test_c

# Test D → Filter on level
python -m test_d

# Test E → Filter limit 20
python -m test_e

# Test F → Get
python -m test_f

# Test I → Update full
python -m test_i

# Test J → Update partial
python -m test_j

# Test K → Delete
python -m test_k
