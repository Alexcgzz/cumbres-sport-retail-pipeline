import os
import time
from decimal import Decimal

import requests
from dotenv import load_dotenv

load_dotenv()
base = os.environ["SAP_BASE_URL"]
client = os.environ["SAP_CLIENT"]

session = requests.Session()
session.auth = (os.environ["SAP_USER"], os.environ["SAP_PASSWORD"])
session.headers.update({"Accept": "application/json"})


def get(path, **params):
    params["sap-client"] = client
    r = session.get(f"{base}/{path}", params=params, timeout=120)
    r.raise_for_status()
    return r.json(parse_float=Decimal)  # importes exactos, no float


# Prueba 1: sin $top, solo una columna. ¿El servidor se corta solo?
d = get("BillingHeader", **{"$select": "vbeln"})
print("Sin $top -> filas:", len(d["value"]),
      "| nextLink:", d.get("@odata.nextLink"))

# Prueba 2: paginación del lado del cliente, con orden estable
PAGE = 5000
skip, rows, total = 0, 0, Decimal("0")
keys = set()
t0 = time.time()

while True:
    d = get("BillingHeader", **{"$top": PAGE, "$skip": skip,
                                "$orderby": "vbeln"})
    batch = d["value"]
    for r in batch:
        keys.add(r["vbeln"])
        total += r["netwr"]
    rows += len(batch)
    skip += PAGE
    print(f"  skip={skip - PAGE:>6}  pagina={len(batch):>5}  acumulado={rows}")
    if len(batch) < PAGE:
        break

print(f"Filas leidas:    {rows}  (esperado 48700)")
print(f"Llaves unicas:   {len(keys)}")
print(f"Suma netwr:      {total}  (esperado 928255270.05)")
print(f"Tiempo:          {time.time() - t0:.1f} s")