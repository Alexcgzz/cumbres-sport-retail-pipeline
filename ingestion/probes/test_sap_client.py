from decimal import Decimal
from sap_client import fetch_pages

rows, total = 0, Decimal("0")
for batch in fetch_pages("BillingHeader", "vbeln"):
    rows += len(batch)
    total += sum(r["netwr"] for r in batch)

print("Filas:", rows, "(esperado 48700)")
print("Suma:", total, "(esperado 928255270.05)")