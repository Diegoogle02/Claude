# Proyecto: Dashboard Liberaciones de Capas — Tr34

## Contexto del Proyecto

Control de obra para construcción vial (carretera). Se trabaja con un sistema de **liberaciones de capas de movimiento de suelos**: cada frente de obra solicita una liberación cuando termina de construir una capa, y las áreas técnicas (Producción, Topografía, Laboratorio, Calidad) firman para aprobarla.

El archivo fuente es un Excel exportado del sistema de gestión con el nombre:
`Liberacion<YYYYMMDDHHM>.xlsx` — hoja: `Reporte Liberaciones`.

---

## Estructura del Excel

| Columna | Descripción |
|---|---|
| Solicitud | Código numérico único de la liberación |
| Fecha de liberación | Fecha en que se solicitó (dd/mm/yyyy) |
| Tramo | Número de tramo (3 o 4) |
| Hito | Código del hito (ej: M181, N221) |
| Calzada | Izquierda / Derecha / Vía de servicio |
| Abscisa Inicial / Final | Puntos kilométricos (enteros, ej: 03640) |
| Capa | Tipo de capa constructiva |
| Ubicación | Capa Inicial / Capa Intermedia / Capa Final / Reproceso |
| Material / Formula | Material específico usado |
| Centro de producción | Planta o cantera de origen |
| Espesor | Espesor en cm |
| Solicitante | Nombre completo del residente que solicita |
| Estado Firmas | Liberado / Pendiente / Solicitud Rechazada |
| Producción / Topografía / Laboratorio / Calidad | Estado de cada firma: Firmado / Pendiente / No Aplica |
| Fecha firma [área] | Timestamp de cada firma |
| Criterio [área] | CUMPLE / NO CUMPLE |
| Motivo de Rechazo | Razón del rechazo si aplica |
| Fecha de creación | Timestamp de creación del registro |

**Metros lineales** = `ABS(Abscisa Final - Abscisa Inicial)`

---

## Reglas de Análisis

### Separación asfalto vs suelos
Siempre excluir del análisis de suelos las siguientes capas:
- `Llegada y extendido de carpeta asfáltica`
- `Control Preliminar - Carpeta Asfaltica`
- `Verificación final carpeta asfáltica`
- `Medición de Indicadores - Carpeta Asfaltica`

El asfalto tiene criterios y ciclos distintos — se analiza por separado cuando se solicite.

### Ciclo de tiempo
El ciclo se mide desde la **firma de Producción** (inicio) hasta la última firma requerida (fin):
- Si `Calidad == 'No Aplica'` → fin = firma de Laboratorio
- Si `Calidad == 'Firmado'` → fin = firma de Calidad

**Capas donde Calidad aplica:** Base, Base Cementada  
**Capas donde Calidad NO aplica:** Terraplén, Subbase, Terreno natural, Corona, Mejoramiento, Cunetas, Lleno de alcantarilla

### Lógica de bloqueante (reporte diario)
El área bloqueante es la primera en el flujo que no tiene estado `Firmado` o `No Aplica`:
1. Producción → 2. Topografía → 3. Laboratorio → 4. Calidad

**Horas esperando** = timestamp actual (o última fecha del archivo) − timestamp de la última firma completada.

### Filtro reporte diario
- Últimas 3 fechas del archivo (por `Fecha de liberación`)
- `Ubicación == 'Capa Final'` para todos los materiales
- `Ubicación == 'Capa Inicial'` solo para `Capa == 'Subbase'` (precede a Base granular)
- Excluir capas asfálticas
- Ordenar pendientes por horas esperando (mayor primero)

---

## Convención de Nombres de Archivos

```
dashboard-liberaciones-DD.MM.MesAA.html
infografico-liberaciones-DD.MM.MesAA.html
reporte-diario-DD.MM.MesAA.html
```

Donde `DD.MM` = fecha de la última solicitud del archivo, `MesAA` = nombre del mes + año corto.

Ejemplo: `dashboard-liberaciones-27.06.Junio26.html`

---

## Outputs Generados por Sesión

| Archivo | Descripción | Audiencia |
|---|---|---|
| `dashboard-liberaciones-*.html` | KPIs, tramos, hitos semáforo, ubicación, solicitantes + gráficos Chart.js | Dirección / Seguimiento mensual |
| `infografico-liberaciones-*.html` | Infográfico vertical: ciclos por capa, semáforo, ranking | Presentaciones / Reportes |
| `reporte-diario-*.html` | Liberaciones pendientes últimas 3 fechas, bloqueantes y horas | Campo / Celular |

---

## Solicitantes Activos (Tr34)

| Nombre | Tramo principal |
|---|---|
| JEKSON SOLANO QUINTERO | T4 |
| Jener VILLEGAS MANOSALVA | T3 y T4 |
| Julio César URIBE VILLA | T3 |
| FERNANDO ALBERTO VEGA NEME | T4 |

---

## Benchmark de Ciclos (Junio 2026)

| Capa | Ciclo promedio | Calidad aplica |
|---|---|---|
| Mejoramiento | 2.2h | No |
| Lleno de alcantarilla | 3.8h | No |
| Subbase | 5.0h | No |
| Corona | 8.6h | No |
| Base | 10.2h | Sí |
| Terraplén | 13.0h | No |
| Base Cementada | 29.7h | Sí |
| Terreno natural | 34.6h | No |

---

## Alertas Conocidas (Junio 2026)

- **Terreno natural** tiene 36% de rechazo — causa principal: lecturas de PDC que no cumplen
- **Laboratorio** tiene 10.7% de NO CUMPLE — principal cuello de botella
- **Hitos N11B, M221, N190** con 0% de liberación — requieren intervención
- **Terraplén en Capa Final** con solo 42% vs 98% en Capa Intermedia — revisar criterio compactación
- **Anomalía de flujo**: en varios registros Laboratorio firmó antes que Topografía
