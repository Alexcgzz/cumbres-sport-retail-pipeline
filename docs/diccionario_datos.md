# Diccionario de datos (simulado)

Los nombres imitan SAP; los datos son sintéticos. Fechas en formato AAAAMMDD, horas HHMMSS.

| Archivo | Tabla SAP imitada | Grano | Campos clave |
|---|---|---|---|
| t001w_stores.csv | T001W | tienda | werks, name1, ort01, regio, region, canal, fecha_apertura |
| mara_materials.csv | MARA/MAKT | material | matnr, maktx, matkl, precio_lista, costo_estandar |
| kna1_customers.csv | KNA1 | cliente | kunnr, name1, ort01, region, fecha_alta |
| posdw_tlogf.csv | /POSDW/TLOGF | línea de ticket | trans_id, linea, werks, fecha, hora, matnr, kunnr, tipo_mov, cantidad, importe_neto |
| vbrk_billing.csv | VBRK | factura por tienda-día | vbeln, fkdat, werks, netwr, mwsbk |
| vbrp_billing_items.csv | VBRP | factura por categoría | vbeln, posnr, matkl, fkimg, netwr, wavwr |
| acdoca_journal.csv | ACDOCA | línea de asiento | belnr, buzei, racct, budat, bldat, prctr, hsl, awref |
| copa_profitability.csv | CO-PA | periodo-tienda-categoría | gjahr, poper, werks, matkl, ingreso_neto, costo_ventas |

## Notas
- `kunnr` vacío en POS = cliente sin programa de lealtad.
- `tipo_mov` = VENTA o DEVOLUCION (importes negativos).
- Cuentas de ACDOCA: 11050000 clientes, 41000000 ventas, 21500000 IVA, 51000000 costo de ventas, 11400000 inventario.
- `awref` en ACDOCA enlaza con `vbeln` de la factura.
- El POS puede traer duplicados exactos y tickets que no llegaron a facturación: son parte del ejercicio.
