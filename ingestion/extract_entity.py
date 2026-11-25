import datetime as dt
import json
import os
import sys
import tempfile
from decimal import Decimal

import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from dotenv import load_dotenv

from entities import ENTITIES, TYPES
from sap_client import count, fetch_pages, fetch_pages_keyset

load_dotenv()
BUCKET = os.environ["S3_BUCKET"]
s3 = boto3.Session(profile_name=os.environ["AWS_PROFILE"]).client("s3")

ROWS_PER_FILE = 100_000


def extract(name):
    cfg = ENTITIES[name]
    schema = pa.schema([(c, TYPES[t][0]) for c, t in cfg["cols"]])
    convs = [(c, TYPES[t][1]) for c, t in cfg["cols"]]
    sum_col = cfg["sum_col"]

    def transform(r):
        return {c: f(r.get(c)) for c, f in convs}

    started = dt.datetime.now(dt.timezone.utc)
    prefix = f"raw/{name}/load_date={started.date().isoformat()}"
    expected = count(cfg["odata"])
    print(f"{cfg['odata']}: SAP reporta {expected} filas")

    state = {"part": 0}
    buffer = []

    def flush():
        if not buffer:
            return
        state["part"] += 1
        table = pa.Table.from_pylist(buffer, schema=schema)
        key = f"{prefix}/part-{state['part']:04d}.parquet"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "part.parquet")
            pq.write_table(table, path)
            s3.upload_file(path, BUCKET, key)
        print(f"  subido s3://{BUCKET}/{key} ({len(buffer)} filas)")
        buffer.clear()

    rows, total = 0, Decimal("0")
    if cfg.get("key"):
        pages = fetch_pages_keyset(cfg["odata"], cfg["key"])
    else:
        pages = fetch_pages(cfg["odata"], cfg["order_by"])
    for batch in pages:
        for r in batch:
            buffer.append(transform(r))
            if sum_col:
                total += Decimal(r[sum_col])
        rows += len(batch)
        if len(buffer) >= ROWS_PER_FILE:
            flush()
    flush()

    problems = []
    if rows != expected:
        problems.append(f"filas {rows} vs {expected}")
    if cfg["expected_sum"] is not None and total != cfg["expected_sum"]:
        problems.append(f"suma {total} vs {cfg['expected_sum']}")

    control = {
        "entity": cfg["odata"], "load_date": started.date().isoformat(),
        "started_utc": started.isoformat(), "rows": rows,
        "expected_rows": expected,
        "sum_col": sum_col, "sum": str(total) if sum_col else None,
        "files": state["part"],
        "status": "failed" if problems else "ok", "problems": problems,
        "finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "seconds": round((dt.datetime.now(dt.timezone.utc) - started).total_seconds(), 1),
    }
    ckey = f"raw/_control/{name}_{started:%Y%m%dT%H%M%S}.json"
    s3.put_object(Bucket=BUCKET, Key=ckey,
                  Body=json.dumps(control, indent=2).encode("utf-8"))
    print(f"  control: {ckey}  status={control['status']}")
    if problems:
        raise RuntimeError(f"{name}: conciliacion fallida: {problems}")
    suma = f", suma {sum_col} = {total}" if sum_col else ""
    print(f"  OK: {rows} filas{suma}")


if __name__ == "__main__":
    # sin argumentos: todo menos POS; con argumentos: solo esas entidades
    names = sys.argv[1:] or [n for n in ENTITIES if n != "posline"]
    for n in names:
        extract(n)