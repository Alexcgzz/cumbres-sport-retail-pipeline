# Arquitectura objetivo

```
SAP (simulado: CDS / OData, delta)
   │  Python: carga inicial + incremental (watermark)
   ▼
AWS S3  raw/ → clean/ → marts/   (Parquet, particionado por fecha)
   │  Glue (catálogo, jobs)  ·  Athena (consultas)
   ▼
SAP HANA Cloud  →  Datasphere (modelos)
   ▼
Power BI (ODBC/OData)   ·   SAC
   ▼
IA: pronóstico por tienda y detección de anomalías
```

## Capas y responsabilidad
| Capa | Qué guarda | Regla |
|---|---|---|
| raw | copia fiel de la fuente | nunca se modifica |
| clean | tipos correctos, duplicados fuera, fechas ISO | reglas de calidad documentadas |
| marts | tablas listas para BI | una cifra, una definición |

## Cargas
- **Inicial (backfill):** histórico completo una vez.
- **Delta:** por fecha de cambio con ventana de traslape de 3 días; carga por upsert para que repetirla no duplique.

## Seguridad
- Secretos en variables de entorno o gestor de secretos; `.env` fuera de Git.
- Usuarios de solo lectura para la fuente; permisos IAM mínimos.

## Observabilidad
- Conteos por carga, alertas por fallo y comparación POS vs facturación vs contabilidad en cada corrida.
