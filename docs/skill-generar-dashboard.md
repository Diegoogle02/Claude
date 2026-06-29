# Skill: /generar-dashboard

Genera el archivo `dashboard-liberaciones-DD.MM.MesAA.html` a partir del análisis del Excel.

## Uso
```
/generar-dashboard
```
Requiere que el Excel ya esté cargado en la sesión (ejecutar `/analizar-liberaciones` antes).

## Qué genera

HTML autocontenido (sin servidor) con tema oscuro y Chart.js CDN, incluyendo:

### Secciones
1. **5 KPI Cards**: Solicitudes totales, ML liberados (%), Tasa de rechazo (%), ML/día promedio, Ciclo mediano
2. **Por Tramo**: Tarjetas con barra de progreso + chips de anomalías + gráfico apilado Chart.js
3. **Por Hito — Semáforo**: Grilla de tarjetas con colores:
   - 🟢 Verde = 100% liberado
   - 🟡 Amarillo = 60–99%
   - 🟠 Naranja = 10–59%
   - 🔴 Rojo = 0% (animación pulse)
4. **Por Ubicación**: Barras tricolor (liberado/rechazado/pendiente) con badges de %
5. **Por Solicitante**: Ranking con barras de progreso y badges "mejor rendimiento" / "mayor rechazo"
6. **Top Rendimientos**: Tarjetas por capa con % y ciclo promedio

### Nombre del archivo
`dashboard-liberaciones-DD.MM.MesAA.html`
- `DD.MM` = día y mes de la última fecha en el archivo
- `MesAA` = nombre del mes en español + año corto (ej: `Junio26`)

## Diseño
- Fondo: `#0f172a` (dark)
- Cards: `#1e293b` con borde `#334155`
- Tipografía: `Segoe UI, system-ui`
- Gráficos: Chart.js 4.4 via CDN
- Max-width: 1400px, responsive grid
