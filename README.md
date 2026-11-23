# Cumbres Sport Retail — Pipeline de datos SAP → AWS → HANA/Datasphere → BI → IA

Proyecto de práctica de ingeniería de datos con el ecosistema SAP. El caso es una cadena
**ficticia** de retail deportivo (44 tiendas + e-commerce) que quiere dejar los reportes en Excel y
tener ventas, margen, conciliación, pronóstico y alertas en una sola plataforma.

> **Los datos son simulados.** Las tablas y campos imitan SAP (T001W, MARA, KNA1, VBRK/VBRP, ACDOCA,
> CO-PA, POS DW) para practicar, pero no provienen de ningún sistema real ni de ninguna empresa.

## Arquitectura (objetivo)
SAP (simulado) → Python (carga inicial + delta) → AWS S3 → Glue → Athena → SAP HANA Cloud + Datasphere
→ Power BI / SAC → capa de IA (pronóstico y anomalías). Detalle en `docs/arquitectura.md`.

## Estado por sprint
| Sprint | Entrega | Estado |
|---|---|---|
| 0 | Entorno, repo, decisiones, datos de retail | En curso |
| 1 | Fuente SAP: CDS y OData con delta | Pendiente |
| 2 | Ingesta a S3 y Glue/Athena | Pendiente |
| 3 | HANA Cloud y Datasphere | Pendiente |
| 4 | Power BI y SAC | Pendiente |
| 5 | IA: pronóstico y anomalías | Pendiente |
| 6 | Operación, pruebas y documentación | Pendiente |

## Cómo generar los datos
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python source_sap/generar_datos_retail.py            # ~1.1 M de líneas de POS
python source_sap/generar_datos_retail.py --ticket-mean 4   # versión ligera
```
Salida en `data/raw/` (ignorada por Git). El archivo `data/_solucion/inyecciones.csv` lista las
anomalías y discrepancias inyectadas: **no lo abras hasta tener tus propias validaciones**.

## Documentación
- `docs/cliente_brief.md` — lo que pide el cliente y los criterios de aceptación
- `docs/decisiones.md` — registro de decisiones (qué, por qué, estado)
- `docs/arquitectura.md` — capas y flujo
- `docs/diccionario_datos.md` — tablas y campos
