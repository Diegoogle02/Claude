# Skill: /generar-infografico

Genera el archivo `infografico-liberaciones-DD.MM.MesAA.html` — infográfico vertical estilo revista, optimizado para scroll.

## Uso
```
/generar-infografico
```
Requiere que el Excel ya esté cargado en la sesión.

## Qué genera

HTML autocontenido, ancho fijo 720px centrado, tema oscuro tipo GitHub/Linear. Sin dependencias externas.

### Secciones en orden vertical

1. **Hero**: título, período, pills de contexto (tramos, solicitudes, ML, nota asfalto)
2. **KPI Strip**: banda horizontal con 5 indicadores en celdas separadas
3. **Ciclos por Capa** *(sección principal)*:
   - Diagrama de flujo: Producción → Topografía → Laboratorio → (Calidad si aplica)
   - Barra segmentada por fase para cada capa (escala proporcional, máx = 40h)
   - Colores: Prod=azul, Topo=violeta, Lab=ámbar, Cal=verde
   - Callouts: más eficiente vs mayor ciclo
4. **Por Tramo**: comparativo con barras y chips de anomalías
5. **Hitos Semáforo**: grilla 4 columnas con punto pulsante en rojos críticos
6. **Por Ubicación**: barras tricolor con track labels
7. **Por Solicitante**: ranking con métricas y barras de color
8. **Hallazgos Críticos**: cajas de alerta por severidad (rojo/amarillo/azul)

### Nombre del archivo
`infografico-liberaciones-DD.MM.MesAA.html`

## Diseño
- Background: `#07090f`
- Surface: `#0d1117` / Cards: `#161b22`
- Tipografía: Google Fonts Inter (300–900)
- Ancho: 720px max, padding lateral 40px
- Separadores de sección con barra de color variable por tema
