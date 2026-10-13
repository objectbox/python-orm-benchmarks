import atexit
import json
import os
from datetime import datetime, timezone

import objectbox.experimental as experimental
from objectbox import (
    Date,
    Entity,
    Float64,
    Id,
    Index,
    Int16,
    Int32,
    Int64,
    Store,
    String,
)

# Experimental FlatBuffers codegen (unreleased objectbox beta) for puts and reads.
# OBX_CODEGEN_CACHE=<dir> caches the compiled code across processes (off by default).
codegen = os.environ.get("OBX_CODEGEN", "1") != "0"
codegen_cache = os.environ.get("OBX_CODEGEN_CACHE") or None
experimental.enable_flatbuffers_codegen(codegen, cache_dir=codegen_cache)
if not codegen:
    ORM_NAME = "ObjectBox (no codegen)"
elif codegen_cache:
    ORM_NAME = "ObjectBox (codegen cache)"
else:
    ORM_NAME = "ObjectBox"

DB_DIR = "/tmp/objectbox-bench"


def now():
    return datetime.now(timezone.utc)


test = int(os.environ.get("TEST", "1"))
if test == 1:

    @Entity()
    class Journal:
        id = Id
        timestamp = Date(datetime)
        level = Int16(index=Index())
        text = String(index=Index())


if test == 2:
    # The Python binding has no relations: these are plain indexed ids, not ORM relations.

    @Entity()
    class Journal:
        id = Id
        timestamp = Date(datetime)
        level = Int16(index=Index())
        text = String(index=Index())
        parent_id = Int64(index=Index())

    @Entity()
    class JournalRelated:
        id = Id
        journal_id = Int64(index=Index())
        journal_from_id = Int64(index=Index())


if test == 3:
    # No per-property defaults: new_journal() sets the defaults of the col_*1/col_*3 sets.
    # No NULL: the "nullable" col_*2/col_*4 sets are left unset (stored as 0/"", read back as None for JSON).
    # No decimal type: decimals are stored as strings. JSON is stored as a JSON string, like the
    # SQL ORMs store it as text; the put/find/get helpers below convert it.
    # (Flex would be the native option, but decodes ~40x slower than json.loads.)

    @Entity()
    class Journal:
        id = Id
        timestamp = Date(datetime)
        level = Int16(index=Index())
        text = String(index=Index())

        col_float1 = Float64
        col_smallint1 = Int16
        col_int1 = Int32
        col_bigint1 = Int64
        col_char1 = String
        col_text1 = String
        col_decimal1 = String
        col_json1 = String

        col_float2 = Float64
        col_smallint2 = Int16
        col_int2 = Int32
        col_bigint2 = Int64
        col_char2 = String
        col_text2 = String
        col_decimal2 = String
        col_json2 = String

        col_float3 = Float64
        col_smallint3 = Int16
        col_int3 = Int32
        col_bigint3 = Int64
        col_char3 = String
        col_text3 = String
        col_decimal3 = String
        col_json3 = String

        col_float4 = Float64
        col_smallint4 = Int16
        col_int4 = Int32
        col_bigint4 = Int64
        col_char4 = String
        col_text4 = String
        col_decimal4 = String
        col_json4 = String

    DEFAULTS = {}
    for n in (1, 3):
        DEFAULTS.update(
            {
                f"col_float{n}": 2.2,
                f"col_smallint{n}": 2,
                f"col_int{n}": 2000000,
                f"col_bigint{n}": 99999999,
                f"col_char{n}": "value1",
                f"col_text{n}": "Moo,Foo,Baa,Waa,Moo,Foo,Baa,Waa,Moo,Foo,Baa,Waa",
                f"col_decimal{n}": "2.2",
            }
        )


def new_journal(**kwargs):
    if test == 3:
        # JSON values are fresh per object, like the other ORMs' JSON defaults
        kwargs = {
            **DEFAULTS,
            "col_json1": {"a": 1, "b": "b", "c": [2], "d": {"e": 3}, "f": True},
            "col_json3": {"a": 1, "b": "b", "c": [2], "d": {"e": 3}, "f": True},
            **kwargs,
        }
    return Journal(timestamp=now(), **kwargs)


JSON_FIELDS = [f"col_json{n}" for n in (1, 2, 3, 4)] if test == 3 else []


_UNSET = object()


def _decode(obj):
    attrs = vars(obj)
    for field in JSON_FIELDS:
        value = attrs.get(field)
        attrs[field] = json.loads(value) if value else None
    return obj


def _encode(obj):
    """Sets the JSON fields to their string form; returns the original values for _restore()."""
    attrs = vars(obj)
    values = [attrs.get(field, _UNSET) for field in JSON_FIELDS]
    for field, value in zip(JSON_FIELDS, values):
        if value is not _UNSET:
            attrs[field] = "" if value is None else json.dumps(value)
    return values


def _restore(obj, values):
    attrs = vars(obj)
    for field, value in zip(JSON_FIELDS, values):
        if value is not _UNSET:
            attrs[field] = value


# The model JSON lives in DB_DIR, so it is wiped (by set_up.py) together with the DB for every TEST
os.makedirs(DB_DIR, exist_ok=True)
store = Store(directory=DB_DIR, model_json_file=os.path.join(DB_DIR, "objectbox-model.json"))
atexit.register(store.close)
box = store.box(Journal)

# Read/write helpers used by the tests; they convert JSON fields eagerly, like an ORM's JSON field
if JSON_FIELDS:

    def put(obj_or_list):
        objs = obj_or_list if isinstance(obj_or_list, list) else [obj_or_list]
        saved = [_encode(obj) for obj in objs]
        try:
            return box.put(obj_or_list)
        finally:
            for obj, values in zip(objs, saved):
                _restore(obj, values)

    def find(query):
        return [_decode(obj) for obj in query.find()]

    def get(id):
        obj = box.get(id)
        return obj if obj is None else _decode(obj)

    def get_all():
        return [_decode(obj) for obj in box.get_all()]

else:
    put = box.put
    get = box.get
    get_all = box.get_all

    def find(query):
        return query.find()
