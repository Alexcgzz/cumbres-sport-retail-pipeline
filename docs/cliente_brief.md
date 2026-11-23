# Brief del cliente — Cumbres Sport Retail (ficticio)

**Quién es:** cadena de retail deportivo con 44 tiendas en México y un e-commerce. Hoy cierra el mes con Excel enviados por correo.

## Qué pide
1. Una sola cifra de ventas y margen que coincida entre punto de venta, facturación y contabilidad.
2. Dashboard de ventas y margen por tienda, región y categoría (Power BI y SAC).
3. Detección de días con ventas anormales y de tickets que no llegaron a facturación.
4. Pronóstico de ventas por tienda a 8 semanas.
5. Cargas diarias incrementales (no recargar todo cada noche).

## Restricciones
- Presupuesto de nube casi cero: usar trials y capas gratuitas, con alerta de gasto.
- Sin credenciales en el repositorio.
- Todo debe poder reconstruirse desde Git.

## Criterios de aceptación
- Conciliación POS vs facturación vs contabilidad con diferencia < 0.5% por tienda-mes, y las diferencias restantes explicadas.
- Las anomalías inyectadas se detectan (se compara contra `data/_solucion/`, solo al final).
- La carga delta no duplica registros al correrla dos veces (idempotencia).
- Dashboard con actualización programada y documentación de cada decisión.
