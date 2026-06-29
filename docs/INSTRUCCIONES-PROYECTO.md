# Instrucciones — Proyecto Tr34 Dashboard Liberaciones

## Estructura del Proyecto

```
/
├── CLAUDE.md                          ← Contexto automático del proyecto
├── .claude/
│   └── commands/
│       ├── analizar-liberaciones.md   ← Skill /analizar-liberaciones
│       ├── generar-dashboard.md       ← Skill /generar-dashboard
│       ├── generar-infografico.md     ← Skill /generar-infografico
│       └── reporte-diario.md          ← Skill /reporte-diario
├── docs/
│   ├── CLAUDE.md                      ← Copia de respaldo
│   ├── skill-*.md                     ← Copias de respaldo de skills
│   └── INSTRUCCIONES-PROYECTO.md     ← Este archivo
├── dashboard-liberaciones-DD.MM.MesAA.html
├── infografico-liberaciones-DD.MM.MesAA.html
└── reporte-diario-DD.MM.MesAA.html
```

---

## Cómo Funciona

### CLAUDE.md (contexto automático)
Claude Code lee automáticamente el archivo `CLAUDE.md` de la raíz del proyecto al iniciar cualquier sesión. Contiene:
- Contexto del proyecto (qué es, para qué sirve)
- Estructura del Excel y reglas de análisis
- Convención de nombres de archivos
- Benchmarks del mes anterior (para comparar)

**No necesitas explicar el proyecto cada vez que empieces una sesión.**

### Skills (comandos slash)
Los archivos en `.claude/commands/` se convierten en comandos `/` dentro de Claude Code.

| Comando | Qué hace |
|---|---|
| `/analizar-liberaciones` | Analiza el Excel y genera el resumen de KPIs, ciclos, hitos |
| `/generar-dashboard` | Genera `dashboard-liberaciones-DD.MM.MesAA.html` |
| `/generar-infografico` | Genera `infografico-liberaciones-DD.MM.MesAA.html` |
| `/reporte-diario` | Genera `reporte-diario-DD.MM.MesAA.html` para campo/celular |

---

## Flujo de Trabajo — Cada Mes

### Paso 1 — Subir el Excel
Arrastra el Excel del mes al chat de Claude Code (o usa `@"ruta/archivo.xlsx"`).

### Paso 2 — Analizar
```
/analizar-liberaciones
```
Claude leerá el Excel y generará el resumen completo. Conversa si necesitas profundizar.

### Paso 3 — Generar los HTMLs
```
/generar-dashboard
/generar-infografico
/reporte-diario
```
Cada comando genera su archivo con el nombre correcto automáticamente:
`dashboard-liberaciones-DD.MM.MesAA.html`

### Paso 4 — Guardar
```
git add . && git commit -m "feat: análisis liberaciones MesAA"
git push
```
O Claude lo hace por ti si se lo pides.

---

## Instalación en Proyecto Nuevo

Si clonas el repositorio en una máquina nueva o abres en Claude Code web:

1. `CLAUDE.md` en la raíz → **se activa solo**, Claude lo lee automáticamente
2. `.claude/commands/` → **se activa solo**, los comandos aparecen al escribir `/`

No se necesita ninguna configuración adicional.

---

## Actualizar el Contexto Cada Mes

Después de cada análisis mensual, actualizar en `CLAUDE.md`:

```markdown
## Benchmark de Ciclos (MesAA)
| Capa | Ciclo promedio | ...

## Alertas Conocidas (MesAA)
- ...
```

Esto hace que el mes siguiente Claude compare contra los datos reales del mes anterior.

---

## Archivos para Google Drive

Carpeta: `claude projects-contextos / Tr34 Dashboard liberaciones`

| Archivo | Propósito en Drive |
|---|---|
| `CLAUDE.md` | Adjuntar al iniciar sesión si no hay acceso al repo |
| `skill-*.md` | Referencia para crear los comandos manualmente |
| `dashboard-liberaciones-*.html` | Abrir en navegador / compartir |
| `infografico-liberaciones-*.html` | Presentaciones / reportes |
| `reporte-diario-*.html` | Compartir por WhatsApp con campo |

> Los `.html` se pueden abrir directamente desde Drive en el navegador — no necesitan servidor.
