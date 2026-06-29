# Skill: /analizar-liberaciones

Analiza un archivo Excel de liberaciones de capas de movimiento de suelos para construcción vial.

## Uso
```
/analizar-liberaciones
```
Luego adjunta o referencia el archivo `.xlsx` exportado del sistema.

## Qué hace

1. **Carga el archivo** y valida que tenga la hoja `Reporte Liberaciones` con el header en fila 3
2. **Calcula metros lineales**: `ABS(Abscisa Final - Abscisa Inicial)`
3. **Separa asfalto** (excluye las 4 capas asfálticas del análisis principal)
4. **Genera KPIs globales**: total solicitudes, ML totales/liberados/rechazados/pendientes, rendimiento diario, ciclo mediano
5. **Analiza por dimensión**: tramo, hito, ubicación, solicitante, capa
6. **Calcula ciclos de tiempo** por tramo del flujo: Producción → Topografía → Laboratorio → Calidad (cuando aplica)
7. **Identifica bloqueantes y anomalías**: orden de firmas fuera de secuencia, hitos con 0% liberación

## Output esperado

Resumen estructurado en texto con:
- KPIs globales
- Tabla por capa (ML, solicitudes, % liberación, ciclo promedio)
- Semáforo de hitos
- Ranking de solicitantes
- Hallazgos críticos

## Reglas importantes

- Excluir siempre: `Llegada y extendido de carpeta asfáltica`, `Control Preliminar - Carpeta Asfaltica`, `Verificación final carpeta asfáltica`, `Medición de Indicadores - Carpeta Asfaltica`
- Ciclo termina en Laboratorio SALVO para Base y Base Cementada (terminan en Calidad)
- Usar `Fecha de liberación` para agrupar por día, `Fecha firma [área]` para ciclos
- Header del Excel está en la fila 3 → usar `header=2` en pandas
