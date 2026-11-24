# Registro de decisiones

Formato: contexto, decisión, por qué, alternativas, estado.

## D-001 — Plataforma SAP: cuenta BTP trial
- **Contexto:** el Advanced Trial no está disponible en México (respuesta de soporte SAP, 20-nov-2026). Se obtuvo acceso con una cuenta trial.
- **Decisión:** usar la cuenta BTP trial como sandbox personal. Inicio 2026-11-23; vence aprox. 2027-02-21.
- **Por qué:** es gratis y no requiere tarjeta. No usar VPN ni números de otro país (riesgo de bloqueo y va contra términos).
- **Riesgo:** Riesgo: el correo asociado a la cuenta podría desactivarse. Mitigación: todo el código y la configuración viven en Git.
- **Estado:** vigente.

## D-002 — Región
- **Decisión:** subcuenta en AWS US East; usar `us-east-1` también en AWS para reducir latencia y costo de transferencia.
- **Estado:** vigente.

## D-003 — Servicios disponibles en el trial (verificado en Derechos)
- Disponibles: HANA Cloud (`hana-free`) y ABAP environment (`abap-trial`).
- No disponibles: Datasphere y SAC.
- **Decisión:** Datasphere/SAC se solicitarán como trial básico de 30 días solo al llegar al Sprint 3, para no gastar los 30 días antes de tener datos.
- Nota: el plan "free" de Datasphere que aparece en videos está deprecado (fin de 2025); usar esos videos solo para conceptos.
- **Estado:** vigente.

## D-004 — Fuente SAP del Sprint 1: sistema ABAP local
- Decisión: usar el sistema local (ABAP con HANA embebida, cliente 001) como fuente simulada.
- Por qué: ya corre, no depende de los límites del trial de BTP y permite practicar CDS, ODP y OData.
- Riesgo: la licencia vence el 21.12.2026; hay que renovarla antes (SLICENSE).
- Plan B: ABAP environment de BTP (límites sin revisar).
- Estado: vigente.

## D-005 — Datos sintéticos con estructura SAP
- **Decisión:** generar datos simulados con nombres de tablas/campos SAP (T001W, MARA, KNA1, VBRK/VBRP, ACDOCA, CO-PA, POS DW) e inyectar fallas conocidas.
- **Por qué:** no hay datos reales; las fallas permiten practicar conciliación y calidad de datos.
- **Estado:** implementada (`source_sap/generar_datos_retail.py`).

## D-006 — Nada se crea en BTP antes de la revisión de diseño
- **Decisión:** no crear instancias en BTP hasta revisar `docs/arquitectura.md`.
- **Por qué:** el trial tiene límites de tiempo y las instancias de HANA Cloud trial pueden detenerse (verificar el comportamiento).
- **Estado:** vigente.

## D-007 — ABAP environment del trial BTP: uso opcional para aprender RAP; no se usa como fuente por ser instancia compartida, sin volumen ni exposición externa confiable, y con vida limitada al trial.
