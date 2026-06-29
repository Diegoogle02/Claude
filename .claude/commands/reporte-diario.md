# Skill: /reporte-diario

Genera el archivo `reporte-diario-DD.MM.MesAA.html` — reporte de campo para celular con liberaciones pendientes de las últimas 3 fechas.

## Uso
```
/reporte-diario
```
Requiere que el Excel ya esté cargado en la sesión.

## Filtro de datos

- **Fechas**: últimas 3 fechas del archivo (por `Fecha de liberación`)
- **Ubicación incluida**:
  - `Capa Final` — todos los materiales (excepto asfalto)
  - `Capa Inicial` — solo `Capa == 'Subbase'` (precede a Base granular)
- **Excluir siempre**: capas asfálticas
- **Estados**: mostrar Pendientes (prioritario) + Liberados (referencia)

## Lógica de bloqueante

Primer área del flujo que NO tiene estado `Firmado` o `No Aplica`:
```
Producción → Topografía → Laboratorio → Calidad
```

**Horas esperando** = última fecha del archivo 23:59 − timestamp de la última firma completada antes del bloqueante.

**Ordenar pendientes**: de más horas a menos (más urgente primero).

**Anomalía a marcar**: si Laboratorio firmó antes que Topografía → mostrar aviso naranja en la tarjeta.

## Qué genera

HTML mobile-first, tema claro (legible en campo/luz solar), sin dependencias externas.

### Header fijo
- Título + rango de fechas
- Strip con 3 indicadores: N° pendientes · ML retenidos · Área crítica

### Tarjetas PENDIENTES (ordenadas por horas)
```
[COLOR ÁREA]                    [⏱ XXh XXmin]
T# · HITO · #CÓDIGO · DD Mes
────────────────────────────
MATERIAL          UBICACIÓN
ABSCISA → ABSCISA         XX ml
────────────────────────────
✅ Prod   ⏳ Topo   ✅ Lab   ➖ Cal
```

**Colores por área bloqueante:**
- Producción: `#2563eb` (azul)
- Topografía: `#6d28d9` (violeta)
- Laboratorio: `#d97706` (ámbar)
- Calidad: `#059669` (verde)

### Tarjetas LIBERADOS
Versión compacta (fondo verde claro) para referencia. Sin detalle de firmas.

### Nombre del archivo
`reporte-diario-DD.MM.MesAA.html`

## Diseño
- Background: `#f0f2f5`
- Cards: `#ffffff` con sombra ligera
- Header sticky: `#111827`
- Tipografía: `-apple-system, BlinkMacSystemFont, 'Segoe UI'`
- Optimizado para pantalla 390px (iPhone) y Android estándar
- `user-scalable=no` para experiencia nativa
