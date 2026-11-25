import datetime as dt
from decimal import Decimal

import pyarrow as pa

S, D, M, I = "string", "date", "money", "int"


def _date(v):
    # SAP manda fechas iniciales como vacio o '0000-...': las guardamos como NULL
    if not v or str(v).startswith("0000"):
        return None
    return dt.date.fromisoformat(v)


# tipo -> (tipo de Arrow, funcion de conversion)
TYPES = {
    S: (pa.string(), lambda v: v),
    D: (pa.date32(), _date),
    M: (pa.decimal128(15, 2), lambda v: None if v is None else Decimal(v)),
    I: (pa.int32(), lambda v: v),
}

ENTITIES = {
    "billing_header": {
        "odata": "BillingHeader", "order_by": "vbeln",
        "cols": [("vbeln", S), ("fkdat", D), ("werks", S), ("netwr", M),
                 ("mwsbk", M), ("waerk", S)],
        "sum_col": "netwr", "expected_sum": Decimal("928255270.05"),
    },
    "billing_item": {
        "odata": "BillingItem", "order_by": "vbeln,posnr",
        "cols": [("vbeln", S), ("posnr", S), ("matkl", S), ("fkimg", I),
                 ("netwr", M), ("wavwr", M), ("waerk", S)],
        "sum_col": "netwr", "expected_sum": Decimal("928255270.05"),
    },
    "journal_entry": {
        "odata": "JournalEntry",
        "order_by": "rldnr,rbukrs,gjahr,belnr,buzei",
        "cols": [("rldnr", S), ("rbukrs", S), ("gjahr", S), ("belnr", S),
                 ("buzei", S), ("racct", S), ("budat", D), ("bldat", D),
                 ("prctr", S), ("hsl", M), ("rhcur", S), ("drcrk", S),
                 ("awtyp", S), ("awref", S)],
        "sum_col": "hsl", "expected_sum": None,
    },
    "profitability": {
        "odata": "Profitability", "order_by": "gjahr,poper,werks,matkl",
        "cols": [("gjahr", S), ("poper", S), ("werks", S), ("matkl", S),
                 ("ingreso_neto", M), ("costo_ventas", M), ("cantidad", I),
                 ("waers", S)],
        "sum_col": "ingreso_neto", "expected_sum": Decimal("928255270.05"),
    },
    "store": {
        "odata": "Store", "order_by": "werks",
        "cols": [("werks", S), ("name1", S), ("ort01", S), ("regio", S),
                 ("region", S), ("canal", S), ("fecha_apertura", D)],
        "sum_col": None, "expected_sum": None,
    },
    "material": {
        "odata": "Material", "order_by": "matnr",
        "cols": [("matnr", S), ("maktx", S), ("matkl", S),
                 ("precio_lista", M), ("costo_estandar", M), ("waers", S)],
        "sum_col": None, "expected_sum": None,
    },
    "customer": {
        "odata": "Customer", "order_by": "kunnr",
        "cols": [("kunnr", S), ("name1", S), ("ort01", S), ("region", S),
                 ("fecha_alta", D)],
        "sum_col": None, "expected_sum": None,
    },
    # POS (1.1 millones de filas): se extrae aparte, con paginacion por llave
    "posline": {
        "odata": "Posline", "order_by": "row_id", "key": "row_id",
        "cols": [("row_id", S), ("trans_id", S), ("linea", S), ("werks", S),
                 ("fecha", D), ("hora", S), ("matnr", S), ("kunnr", S),
                 ("tipo_mov", S), ("cantidad", I), ("precio_unitario", M),
                 ("descuento_pct", I), ("importe_neto", M), ("moneda", S)],
        "sum_col": "importe_neto", "expected_sum": Decimal("928802834.80"),
    },
}