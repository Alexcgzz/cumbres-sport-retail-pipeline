# Modelo CDS y servicio OData — versión final (Sprint 1B)

Fuente de verdad del modelo que vive en el SAP local. Los objetos se crean en ADT (paquete `$ZCSR_SOURCE`); este archivo permite reconstruirlos.

Orden de creación: primero `ZI_CSR_BILLINGITEM` (la cabecera depende de ella), luego las demás vistas, luego la definición de servicio y el binding.

Nombres ODP resultantes (RODPS_REPL_TEST, contexto ABAP_CDS): `$F` para hechos y `$P` para datos maestros, p. ej. `ZI_CSR_PROFITABILITY$F`, `ZI_CSR_STORE$P`.

## ZI_CSR_BILLINGITEM  (sobre `zcsr_vbrp`, categoría FACT)
```
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Billing Item'
@Metadata.ignorePropagatedAnnotations: true
@Analytics.dataExtraction.enabled: true
@Analytics.dataCategory: #FACT
define view entity ZI_CSR_BILLINGITEM
  as select from zcsr_vbrp
{
  key vbeln,
  key posnr,
      matkl,
      fkimg,
      @Semantics.amount.currencyCode: 'waerk'
      netwr,
      @Semantics.amount.currencyCode: 'waerk'
      wavwr,
      waerk
}
```

## ZI_CSR_BILLINGHEADER  (sobre `zcsr_vbrk`, categoría FACT)
```
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Billing Header'
@Metadata.ignorePropagatedAnnotations: true
@Analytics.dataExtraction.enabled: true
@Analytics.dataCategory: #FACT
define view entity ZI_CSR_BILLINGHEADER
  as select from zcsr_vbrk
  association [0..*] to ZI_CSR_BILLINGITEM as _Item
    on $projection.vbeln = _Item.vbeln
{
  key vbeln,
      fkdat,
      werks,
      @Semantics.amount.currencyCode: 'waerk'
      netwr,
      @Semantics.amount.currencyCode: 'waerk'
      mwsbk,
      waerk,
      _Item
}
```

## ZI_CSR_POSLINE  (sobre `zcsr_tlogf`, categoría FACT)
```
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'POS Transaction Line'
@Metadata.ignorePropagatedAnnotations: true
@Analytics.dataExtraction.enabled: true
@Analytics.dataCategory: #FACT
define view entity ZI_CSR_POSLINE
  as select from zcsr_tlogf
{
  key row_id,
      trans_id,
      linea,
      werks,
      fecha,
      hora,
      matnr,
      kunnr,
      tipo_mov,
      cantidad,
      @Semantics.amount.currencyCode: 'moneda'
      precio_unitario,
      descuento_pct,
      @Semantics.amount.currencyCode: 'moneda'
      importe_neto,
      moneda
}
```

## ZI_CSR_JOURNALENTRY  (sobre `zcsr_acdoca`, categoría FACT)
```
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Journal Entry Line'
@Metadata.ignorePropagatedAnnotations: true
@Analytics.dataExtraction.enabled: true
@Analytics.dataCategory: #FACT
define view entity ZI_CSR_JOURNALENTRY
  as select from zcsr_acdoca
{
  key rldnr,
  key rbukrs,
  key gjahr,
  key belnr,
  key buzei,
      racct,
      budat,
      bldat,
      prctr,
      @Semantics.amount.currencyCode: 'rhcur'
      hsl,
      rhcur,
      drcrk,
      awtyp,
      awref
}
```

## ZI_CSR_PROFITABILITY  (sobre `zcsr_copa`, categoría FACT)
```
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Profitability'
@Metadata.ignorePropagatedAnnotations: true
@Analytics.dataExtraction.enabled: true
@Analytics.dataCategory: #FACT
define view entity ZI_CSR_PROFITABILITY
  as select from zcsr_copa
{
  key gjahr,
  key poper,
  key werks,
  key matkl,
      @Semantics.amount.currencyCode: 'waers'
      ingreso_neto,
      @Semantics.amount.currencyCode: 'waers'
      costo_ventas,
      cantidad,
      waers
}
```

## ZI_CSR_STORE  (sobre `zcsr_t001w`, categoría DIMENSION)
```
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Store'
@Metadata.ignorePropagatedAnnotations: true
@Analytics.dataExtraction.enabled: true
@Analytics.dataCategory: #DIMENSION
define view entity ZI_CSR_STORE
  as select from zcsr_t001w
{
  key werks,
      name1,
      ort01,
      regio,
      region,
      canal,
      fecha_apertura
}
```

## ZI_CSR_MATERIAL  (sobre `zcsr_mara`, categoría DIMENSION)
```
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Material'
@Metadata.ignorePropagatedAnnotations: true
@Analytics.dataExtraction.enabled: true
@Analytics.dataCategory: #DIMENSION
define view entity ZI_CSR_MATERIAL
  as select from zcsr_mara
{
  key matnr,
      maktx,
      matkl,
      @Semantics.amount.currencyCode: 'waers'
      precio_lista,
      @Semantics.amount.currencyCode: 'waers'
      costo_estandar,
      waers
}
```

## ZI_CSR_CUSTOMER  (sobre `zcsr_kna1`, categoría DIMENSION)
```
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Customer'
@Metadata.ignorePropagatedAnnotations: true
@Analytics.dataExtraction.enabled: true
@Analytics.dataCategory: #DIMENSION
define view entity ZI_CSR_CUSTOMER
  as select from zcsr_kna1
{
  key kunnr,
      name1,
      ort01,
      region,
      fecha_alta
}
```

## Definición de servicio: ZSD_CSR_SALES
```
@EndUserText.label: 'Cumbres Sport Retail - Sales'
define service ZSD_CSR_SALES {
  expose ZI_CSR_BILLINGHEADER as BillingHeader;
  expose ZI_CSR_BILLINGITEM   as BillingItem;
  expose ZI_CSR_POSLINE       as Posline;
  expose ZI_CSR_JOURNALENTRY  as JournalEntry;
  expose ZI_CSR_PROFITABILITY as Profitability;
  expose ZI_CSR_STORE         as Store;
  expose ZI_CSR_MATERIAL      as Material;
  expose ZI_CSR_CUSTOMER      as Customer;
}
```

## Service Binding: ZSB_CSR_SALES_V4
- Tipo: OData V4 - Web API, publicado.
- Ruta: `/sap/opu/odata4/sap/zsb_csr_sales_v4/srvd_a2x/sap/zsd_csr_sales/0001/`
- Verificación: `BillingHeader/$count` devuelve 48700 (navegador, `http://localhost:50000`).
