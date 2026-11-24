"""Totales de los CSV generados. Compáralos con lo que imprime el cargador ABAP en SAP.

Uso (desde la raíz del repo):  python source_sap/resumen_csv.py
"""
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "raw")


def leer(nombre):
    return pd.read_csv(os.path.join(D, nombre), dtype=str, keep_default_na=False)


def suma(serie):
    return f"{serie.astype(float).sum():.2f}"


t = leer("t001w_stores.csv");        print(f"ZCSR_T001W filas: {len(t)}")
m = leer("mara_materials.csv");      print(f"ZCSR_MARA filas: {len(m)}")
k = leer("kna1_customers.csv");      print(f"ZCSR_KNA1 filas: {len(k)}")
p = leer("posdw_tlogf.csv");         print(f"ZCSR_TLOGF filas: {len(p)} | importe_neto: {suma(p['importe_neto'])}")
h = leer("vbrk_billing.csv");        print(f"ZCSR_VBRK filas: {len(h)} | netwr: {suma(h['netwr'])}")
i = leer("vbrp_billing_items.csv");  print(f"ZCSR_VBRP filas: {len(i)} | netwr: {suma(i['netwr'])}")
a = leer("acdoca_journal.csv")
ventas = a[a["racct"] == "41000000"]
print(f"ZCSR_ACDOCA filas: {len(a)} | hsl cuenta 41000000: {suma(ventas['hsl'])}")
c = leer("copa_profitability.csv");  print(f"ZCSR_COPA filas: {len(c)} | ingreso_neto: {suma(c['ingreso_neto'])}")
