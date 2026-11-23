"""
Generador de datos sintéticos — Cumbres Sport Retail (proyecto de práctica).

Simula, con estructura tipo SAP, los datos de una cadena ficticia de retail
deportivo (44 tiendas + comercio electrónico) durante ~3 años:

  t001w_stores.csv      Tiendas / centros              (T001W)
  mara_materials.csv    Materiales                     (MARA/MAKT)
  kna1_customers.csv    Clientes (lealtad y e-commerce)(KNA1)
  posdw_tlogf.csv       Líneas de ticket del punto de venta (estilo /POSDW/TLOGF)
  vbrk_billing.csv      Facturas: cabecera, una por tienda y día (VBRK)
  vbrp_billing_items.csv Facturas: posiciones por categoría (VBRP)
  acdoca_journal.csv    Asientos contables (ACDOCA)
  copa_profitability.csv Rentabilidad por periodo/tienda/categoría (CO-PA)

IMPORTANTE: son datos SIMULADOS. Los nombres de tablas y campos imitan SAP
para practicar, pero no provienen de ningún sistema real.

Imperfecciones inyectadas a propósito (para que el pipeline las detecte):
  - Anomalías de ventas (cierres, picos, caídas) en días puntuales.
  - Caídas de comunicación: tickets del POS que nunca llegan a facturación.
  - Líneas duplicadas por reenvío en el POS.
  - Asientos contables registrados con 1-3 días de retraso (desfase de periodo).
  - Fechas y horas en formato SAP (AAAAMMDD, HHMMSS) y clientes vacíos.
La lista exacta está en data/_solucion/inyecciones.csv. NO la abras hasta
haber construido tus propias validaciones.

Uso:
    python source_sap/generar_datos_retail.py
    python source_sap/generar_datos_retail.py --ticket-mean 4   # versión ligera
"""

import argparse
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IVA = 0.16

# ---------------------------------------------------------------------------
# Catálogos
# ---------------------------------------------------------------------------
CIUDADES = [
    ("Monterrey", "Nuevo León", "Norte"), ("San Pedro Garza García", "Nuevo León", "Norte"),
    ("Guadalupe", "Nuevo León", "Norte"), ("Saltillo", "Coahuila", "Norte"),
    ("Torreón", "Coahuila", "Norte"), ("Chihuahua", "Chihuahua", "Norte"),
    ("Tijuana", "Baja California", "Norte"), ("Hermosillo", "Sonora", "Norte"),
    ("Culiacán", "Sinaloa", "Norte"), ("Ciudad de México", "Ciudad de México", "Centro"),
    ("Toluca", "Estado de México", "Centro"), ("Puebla", "Puebla", "Centro"),
    ("Cuernavaca", "Morelos", "Centro"), ("Querétaro", "Querétaro", "Bajío"),
    ("León", "Guanajuato", "Bajío"), ("Aguascalientes", "Aguascalientes", "Bajío"),
    ("San Luis Potosí", "San Luis Potosí", "Bajío"), ("Guadalajara", "Jalisco", "Occidente"),
    ("Zapopan", "Jalisco", "Occidente"), ("Morelia", "Michoacán", "Occidente"),
    ("Mérida", "Yucatán", "Sureste"), ("Cancún", "Quintana Roo", "Sureste"),
    ("Veracruz", "Veracruz", "Sureste"), ("Villahermosa", "Tabasco", "Sureste"),
]
N_TIENDAS = 44

# categoría: (peso en catálogo, precio mediano sin IVA, dispersión, factor de costo)
CATEGORIAS = {
    "Calzado": (0.34, 1300, 0.45, 0.55),
    "Ropa": (0.36, 450, 0.40, 0.45),
    "Accesorios": (0.14, 220, 0.45, 0.40),
    "Equipo deportivo": (0.10, 800, 0.55, 0.60),
    "Nutrición": (0.06, 350, 0.35, 0.65),
}
TIPOS = {
    "Calzado": ["Tenis running", "Tenis training", "Tenis casual", "Tenis futbol", "Bota outdoor"],
    "Ropa": ["Playera", "Short", "Sudadera", "Leggings", "Chamarra", "Pants"],
    "Accesorios": ["Mochila", "Gorra", "Calcetas", "Botella", "Guantes"],
    "Equipo deportivo": ["Balón", "Raqueta", "Pesas", "Tapete de yoga", "Cuerda de salto"],
    "Nutrición": ["Proteína", "Creatina", "Barras", "Electrolitos"],
}
MARCAS = ["Nike", "Adidas", "Puma", "Under Armour", "New Balance", "Reebok", "Marca propia"]

DOW_W = np.array([0.85, 0.85, 0.90, 0.95, 1.15, 1.35, 1.25])           # lun..dom
MES_W = {1: .90, 2: .85, 3: .95, 4: .95, 5: 1.05, 6: 1.0, 7: .95,
         8: 1.15, 9: .95, 10: 1.0, 11: 1.20, 12: 1.40}


def fechas_evento(days):
    """Marca Buen Fin (vie-lun de la 3.ª semana de nov.) y Hot Sale (27-29 may., aprox.)."""
    buen_fin = np.zeros(len(days), bool)
    hot_sale = np.zeros(len(days), bool)
    for y in range(days[0].year, days[-1].year + 1):
        viernes = next(d for d in pd.date_range(f"{y}-11-13", f"{y}-11-19") if d.dayofweek == 4)
        buen_fin |= (days >= viernes) & (days <= viernes + pd.Timedelta(days=3))
        hot_sale |= (days >= pd.Timestamp(f"{y}-05-27")) & (days <= pd.Timestamp(f"{y}-05-29"))
    return buen_fin, hot_sale


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "raw"))
    ap.add_argument("--ticket-mean", type=float, default=10.0,
                    help="tickets promedio por tienda y día (sube el volumen; default 10)")
    ap.add_argument("--start", default="2023-11-01")
    ap.add_argument("--end", default="2026-11-21")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    out = args.out
    sol = os.path.join(os.path.dirname(out), "_solucion")
    os.makedirs(out, exist_ok=True)
    os.makedirs(sol, exist_ok=True)
    inyecciones = []          # registro de todo lo que se inyecta

    days = pd.date_range(args.start, args.end)
    nd = len(days)
    dow, month = days.dayofweek.values, days.month.values
    years = (days - days[0]).days.values / 365.25
    buen_fin, hot_sale = fechas_evento(days)
    promo = buen_fin | hot_sale
    evento_mult = np.where(buen_fin, 1.7, np.where(hot_sale, 1.35, 1.0))
    day_str = np.array([d.strftime("%Y%m%d") for d in days])

    # ------------------------------------------------------------------ tiendas
    stores = []
    for i in range(N_TIENDAS):
        ciudad, estado, region = CIUDADES[i % len(CIUDADES)]
        k = i // len(CIUDADES) + 1
        repetida = (i % len(CIUDADES)) < (N_TIENDAS - len(CIUDADES))   # ciudades con 2 tiendas
        nombre = f"Cumbres {ciudad}" + (f" {k}" if repetida else "")
        stores.append([f"T{i+1:03d}", nombre, ciudad, estado, region, "TIENDA", None])
    stores.append(["E001", "Cumbres E-commerce", "Monterrey", "Nuevo León", "Norte", "ECOMMERCE", None])
    S = len(stores)
    ecom_idx = S - 1
    size = np.clip(rng.normal(1.0, 0.35, S), 0.5, 2.0)
    open_date = np.full(S, days[0] - pd.Timedelta(days=400), dtype="datetime64[ns]")
    nuevas = rng.choice(np.arange(N_TIENDAS - 6, N_TIENDAS), size=4, replace=False)
    for j in nuevas:     # 4 tiendas abren durante el periodo
        open_date[j] = days[0] + pd.Timedelta(days=int(rng.integers(120, 700)))
    for i in range(S):
        stores[i][6] = pd.Timestamp(open_date[i]).strftime("%Y%m%d")
    pd.DataFrame(stores, columns=["werks", "name1", "ort01", "regio", "region", "canal", "fecha_apertura"]) \
        .to_csv(os.path.join(out, "t001w_stores.csv"), index=False)
    open_mask = (days.values[None, :] >= open_date[:, None]).astype(float)

    # --------------------------------------------------------------- materiales
    NM = 600
    cats = list(CATEGORIAS)
    mcat = rng.choice(cats, size=NM, p=[CATEGORIAS[c][0] for c in cats])
    precio = np.zeros(NM); costo = np.zeros(NM); maktx = []
    for i, c in enumerate(mcat):
        _, med, sig, fc = CATEGORIAS[c]
        p = rng.lognormal(np.log(med), sig)
        precio[i] = max(49, round(p / 10) * 10 - 1)                 # termina en 9
        costo[i] = round(precio[i] * fc * rng.uniform(0.92, 1.08), 2)
        maktx.append(f"{rng.choice(TIPOS[c])} {rng.choice(MARCAS)} {rng.integers(100, 999)}")
    matnr = np.array([f"M{i+1:06d}" for i in range(NM)])
    pd.DataFrame({"matnr": matnr, "maktx": maktx, "matkl": mcat, "precio_lista": precio,
                  "costo_estandar": costo, "waers": "MXN"}) \
        .to_csv(os.path.join(out, "mara_materials.csv"), index=False)
    pop = rng.pareto(1.3, NM) + 1
    pop /= pop.sum()

    # ----------------------------------------------------------------- clientes
    NC = 20000
    kunnr_all = np.array([f"K{i+1:07d}" for i in range(NC)])
    ciu = rng.integers(0, len(CIUDADES), NC)
    pd.DataFrame({"kunnr": kunnr_all, "name1": [f"CLIENTE {i+1:07d}" for i in range(NC)],
                  "ort01": [CIUDADES[j][0] for j in ciu], "region": [CIUDADES[j][2] for j in ciu],
                  "fecha_alta": day_str[rng.integers(0, nd, NC)]}) \
        .to_csv(os.path.join(out, "kna1_customers.csv"), index=False)

    # -------------------------------------------------- tickets por tienda y día
    media = np.zeros((S, nd))
    for s in range(N_TIENDAS):
        media[s] = args.ticket_mean * size[s] * (1.07 ** years) * DOW_W[dow] \
                   * np.array([MES_W[m] for m in month]) * evento_mult
    media[ecom_idx] = args.ticket_mean * 3.5 * (1.25 ** years) \
                      * np.where(dow >= 5, 1.1, 1.0) * np.array([MES_W[m] for m in month]) \
                      * np.where(promo, 2.0, 1.0)
    media *= open_mask

    # anomalías inyectadas (solo tiendas, fuera de eventos)
    cand = [(s, d) for s in range(N_TIENDAS) for d in range(40, nd)
            if open_mask[s, d] > 0 and not promo[d]]
    elegidas = rng.choice(len(cand), size=25, replace=False)
    tipos_an = ["cierre"] * 10 + ["pico"] * 8 + ["caida"] * 7
    factor = {"cierre": 0.0, "pico": 2.6, "caida": 0.4}
    for k, t in zip(elegidas, tipos_an):
        s, d = cand[k]
        media[s, d] *= factor[t]
        inyecciones.append(["anomalia_ventas", stores[s][0], day_str[d], t, f"factor={factor[t]}"])

    n = rng.poisson(media)
    s_idx, d_idx = np.nonzero(n)
    cnt = n[s_idx, d_idx]
    t_s, t_d = np.repeat(s_idx, cnt), np.repeat(d_idx, cnt)
    order = np.lexsort((t_s, t_d))
    t_s, t_d = t_s[order], t_d[order]
    N = len(t_s)
    es_ecom = t_s == ecom_idx

    h = np.where(es_ecom, rng.choice(np.arange(8, 24), size=N), 0)
    h_t = rng.choice(np.arange(10, 22), size=N, p=np.array([2, 3, 4, 5, 5, 5, 6, 7, 8, 8, 6, 3]) / 62)
    h = np.where(es_ecom, h, h_t)
    hora = (h * 10000 + rng.integers(0, 60, N) * 100 + rng.integers(0, 60, N)).astype(str)
    hora = pd.Series(hora).str.zfill(6).values

    lealtad = es_ecom | (rng.random(N) < 0.35)
    cidx = np.minimum((rng.pareto(1.2, N) * 500).astype(int), NC - 1)
    kunnr_t = np.where(lealtad, kunnr_all[cidx], "")

    nl = np.clip(1 + rng.poisson(np.where(es_ecom, 0.6, 0.7)), 1, 6)
    L = nl.sum()
    line_t = np.repeat(np.arange(N), nl)
    posnr = np.arange(L) - np.repeat(np.cumsum(nl) - nl, nl) + 1
    midx = rng.choice(NM, size=L, p=pop)
    qty = rng.choice([1, 2, 3], size=L, p=[0.80, 0.15, 0.05])
    en_promo = promo[t_d[line_t]]
    desc = np.where(en_promo,
                    rng.choice([0, .2, .3, .4], size=L, p=[.15, .35, .30, .20]),
                    rng.choice([0, .1, .15, .2], size=L, p=[.75, .12, .08, .05]))
    neto = np.round(qty * precio[midx] * (1 - desc), 2)
    devol = rng.random(L) < 0.025
    qty = np.where(devol, -qty, qty)
    neto = np.where(devol, -neto, neto)
    ls, ld = t_s[line_t], t_d[line_t]

    # caídas de comunicación: líneas que nunca llegan a facturación
    perdida = np.zeros(L, bool)
    pares = np.unique(np.stack([ls, ld], 1), axis=0)
    pares = pares[pares[:, 0] != ecom_idx]
    for k in rng.choice(len(pares), size=8, replace=False):
        s, d = pares[k]
        frac = rng.uniform(0.4, 1.0)
        m = (ls == s) & (ld == d) & (rng.random(L) < frac)
        perdida |= m
        inyecciones.append(["caida_comunicacion", stores[s][0], day_str[d],
                            "no_llego_a_facturacion", f"monto_perdido={neto[m].sum():.2f}"])

    pos = pd.DataFrame({
        "trans_id": line_t + 1, "linea": posnr, "werks": np.array([x[0] for x in stores])[ls],
        "fecha": day_str[ld], "hora": hora[line_t], "matnr": matnr[midx], "kunnr": kunnr_t[line_t],
        "tipo_mov": np.where(devol, "DEVOLUCION", "VENTA"), "cantidad": qty,
        "precio_unitario": precio[midx], "descuento_pct": (desc * 100).round(0).astype(int),
        "importe_neto": neto, "moneda": "MXN"})
    # duplicados por reenvío
    dup_i = rng.choice(L, size=int(L * 0.0005), replace=False)
    dup = pos.iloc[dup_i].copy()
    for _, r in dup.iterrows():
        inyecciones.append(["duplicado_pos", r["werks"], r["fecha"], f"trans_id={r['trans_id']}",
                            f"linea={r['linea']};importe={r['importe_neto']}"])
    pos_out = pd.concat([pos, dup]).sort_values(["fecha", "trans_id", "linea"], kind="stable")
    pos_out.to_csv(os.path.join(out, "posdw_tlogf.csv"), index=False)

    # ------------------------------------------------------------- facturación
    ok = ~perdida
    b = pd.DataFrame({"s": ls[ok], "d": ld[ok], "cat": mcat[midx][ok], "qty": qty[ok],
                      "neto": neto[ok], "cogs": np.round(qty[ok] * costo[midx][ok], 2)})
    hdr = b.groupby(["d", "s"], as_index=False).agg(netwr=("neto", "sum"), cogs=("cogs", "sum"))
    hdr["vbeln"] = (9_000_000_000 + np.arange(1, len(hdr) + 1)).astype(str)
    hdr["werks"] = np.array([x[0] for x in stores])[hdr["s"].values]
    hdr["fkdat"] = day_str[hdr["d"].values]
    hdr["netwr"] = hdr["netwr"].round(2)
    hdr["mwsbk"] = (hdr["netwr"] * IVA).round(2)
    hdr["cogs"] = hdr["cogs"].round(2)
    pd.DataFrame({"vbeln": hdr["vbeln"], "fkart": "F2", "fkdat": hdr["fkdat"], "werks": hdr["werks"],
                  "netwr": hdr["netwr"], "mwsbk": hdr["mwsbk"], "waerk": "MXN"}) \
        .to_csv(os.path.join(out, "vbrk_billing.csv"), index=False)

    items = b.groupby(["d", "s", "cat"], as_index=False).agg(
        fkimg=("qty", "sum"), netwr=("neto", "sum"), wavwr=("cogs", "sum"))
    items = items.merge(hdr[["d", "s", "vbeln"]], on=["d", "s"])
    items = items.sort_values(["vbeln", "cat"])
    items["posnr"] = items.groupby("vbeln").cumcount() + 1
    pd.DataFrame({"vbeln": items["vbeln"], "posnr": items["posnr"], "matkl": items["cat"],
                  "fkimg": items["fkimg"], "netwr": items["netwr"].round(2),
                  "wavwr": items["wavwr"].round(2)}) \
        .to_csv(os.path.join(out, "vbrp_billing_items.csv"), index=False)

    # -------------------------------------------------------------- contabilidad
    M = len(hdr)
    retraso = np.where(rng.random(M) < 0.003, rng.integers(1, 4, M), 0)
    budat = days[hdr["d"].values] + pd.to_timedelta(retraso, unit="D")
    for i in np.nonzero(retraso)[0]:
        inyecciones.append(["asiento_con_retraso", hdr["werks"].iloc[i], hdr["fkdat"].iloc[i],
                            f"vbeln={hdr['vbeln'].iloc[i]}", f"dias_retraso={retraso[i]}"])
    belnr = (4_900_000_000 + np.arange(1, M + 1)).astype(str)
    cuentas = ["11050000", "41000000", "21500000", "51000000", "11400000"]
    drcrk = ["S", "H", "H", "S", "H"]
    montos = np.stack([hdr["netwr"] + hdr["mwsbk"], -hdr["netwr"], -hdr["mwsbk"],
                       hdr["cogs"], -hdr["cogs"]], 1).round(2)
    rep = lambda a: np.repeat(a, 5)
    acd = pd.DataFrame({
        "rldnr": "0L", "rbukrs": "1000", "gjahr": rep(budat.year.values), "belnr": rep(belnr),
        "buzei": np.tile(np.arange(1, 6), M), "racct": np.tile(cuentas, M),
        "budat": rep(budat.strftime("%Y%m%d").values), "bldat": rep(hdr["fkdat"].values),
        "prctr": rep(hdr["werks"].values), "hsl": montos.reshape(-1),
        "drcrk": np.tile(drcrk, M), "awtyp": "VBRK", "awref": rep(hdr["vbeln"].values)})
    acd.to_csv(os.path.join(out, "acdoca_journal.csv"), index=False)

    # -------------------------------------------------------------------- CO-PA
    items["fecha"] = pd.to_datetime(day_str[items["d"].values], format="%Y%m%d")
    items["werks"] = np.array([x[0] for x in stores])[items["s"].values]
    copa = items.assign(gjahr=items["fecha"].dt.year, poper=items["fecha"].dt.month.map(lambda m: f"{m:03d}")) \
        .groupby(["gjahr", "poper", "werks", "cat"], as_index=False) \
        .agg(ingreso_neto=("netwr", "sum"), costo_ventas=("wavwr", "sum"), cantidad=("fkimg", "sum"))
    copa = copa.rename(columns={"cat": "matkl"}).round(2)
    copa.to_csv(os.path.join(out, "copa_profitability.csv"), index=False)

    pd.DataFrame(inyecciones, columns=["tipo", "werks", "fecha", "detalle", "valor"]) \
        .to_csv(os.path.join(sol, "inyecciones.csv"), index=False)

    # ------------------------------------------------------------------ resumen
    rev_pos = pos["importe_neto"].sum()
    rev_pos_dup = pos_out["importe_neto"].sum()
    rev_bill = hdr["netwr"].sum()
    rev_fi = -acd.loc[acd["racct"] == "41000000", "hsl"].sum()
    print(f"Tickets: {N:,} | líneas POS: {len(pos_out):,} | facturas: {M:,} | asientos: {len(acd):,}")
    print(f"Ventas netas (MXN)  POS limpio: {rev_pos:,.0f} | POS con duplicados: {rev_pos_dup:,.0f}")
    print(f"                    Facturación: {rev_bill:,.0f} | Contabilidad (41000000): {rev_fi:,.0f}")
    print(f"Dif. POS limpio vs facturación: {(rev_pos-rev_bill)/rev_pos:.4%} | "
          f"facturación vs contabilidad: {(rev_bill-rev_fi)/rev_bill:.6%}")
    print(f"Margen bruto global: {1 - hdr['cogs'].sum()/rev_bill:.1%}")
    anio = hdr.groupby(pd.Series(days[hdr["d"].values].year, index=hdr.index))["netwr"].sum()
    print("Ventas por año (M):", {int(k): round(v / 1e6, 1) for k, v in anio.items()})
    print(f"Inyecciones registradas: {len(inyecciones)} (data/_solucion/inyecciones.csv)")


if __name__ == "__main__":
    main()
