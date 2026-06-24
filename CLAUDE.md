# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static HTML/CSS/JS design system and dashboard prototype for **Control de Obra** — a construction materials tracking application for the "Ruta del Sol" highway project (Tramos 3 and 4, Colombia). There is no build step, no package manager, and no backend. Open `design-system/index.html` directly in a browser to view it.

## Architecture

The design system is split into three files that must be loaded in order:

1. **`variables.css`** — Single source of truth for all design tokens: color palette, typography scale, spacing scale (base 4 px), border radii, shadows, transitions, layout constants (`--sidebar-w`, `--navbar-h`), and z-index ladder. **Never hard-code values that belong here.**

2. **`components.css`** — All reusable component styles (buttons, inputs, badges, chips, cards, KPI cards, table, navbar, sidebar, modal, toast, progress bar, empty state, layout shell, animations, responsive breakpoints). Components reference variables exclusively via `var(--…)`.

3. **`index.html`** — Assembles the full dashboard. Contains page-specific styles in a `<style>` block and all JavaScript (Chart.js charts, modal, sidebar toggle, toast, chip filters, table rendering). Chart.js is loaded from CDN (`cdn.jsdelivr.net/npm/chart.js@4.4.0`).

## CSS naming conventions

| Pattern | Purpose |
|---|---|
| `--c-*` | Color tokens (`--c-primary`, `--c-ink`, `--c-border`, etc.) |
| `--text-*` | Font-size scale (`--text-xs` through `--text-4xl`) |
| `--w-*` | Font-weight tokens (`--w-regular` → `--w-extrabold`) |
| `--sp-*` | Spacing scale in multiples of 4 px (`--sp-1` = 4 px … `--sp-16` = 64 px) |
| `--r-*` | Border-radius tokens (`--r-xs` through `--r-full`) |
| `--sh-*` | Box-shadow tokens (`--sh-xs` through `--sh-xl`) |
| `--z-*` | Z-index tokens (`--z-base` → `--z-toast: 300`) |
| `--ease-*` | Transition shorthand tokens |

## Component conventions

- **Buttons**: `.btn` base + variant modifier (`.btn-primary`, `.btn-ghost`, `.btn-danger`, `.btn-success`) + optional size (`.btn-sm`, `.btn-lg`). Loading state via `.btn-loading`.
- **Badges**: `.badge` + status modifier (`.badge-liberado`, `.badge-pendiente`, `.badge-rechazado`, `.badge-aprobado`, `.badge-ejecutado`). Each badge auto-renders a dot via `::before`.
- **Chips** (filter toggles): `.chip`; active state toggles to `.active`, `.active-tr3`, or `.active-tr4` to apply the correct colour for the selected tramo.
- **KPI cards**: `.card.kpi-card` + colour modifier (`.primary`, `.success`, `.warning`, `.error`, `.blue`, `.teal`, `.purple`). The coloured left border and `kpi-value` colour are both driven by the modifier class.
- **Progress bars**: `.progress-bar` wrapper + `.progress-fill` with a status modifier (`.success`, `.warning`, `.error`, `.primary`). Set `style="width: X%"` inline.
- **Toasts**: Created dynamically via `showToast(msg, type)`. The container `#toastContainer` is fixed bottom-right at `z-index: var(--z-toast)`.

## Layout shell

```
<aside class="sidebar">          fixed left, 240 px wide, dark background
<header class="navbar">         fixed top, offset by sidebar-w, 58 px tall
<div class="app-shell">
  <main class="main-content">  margin-left: sidebar-w, padding-top: navbar-h
    <div class="page">          max-width 1400 px, padded content area
```

On mobile (`≤ 768 px`) the sidebar hides offscreen and slides in when `.open` is toggled via `toggleSidebar()`. An overlay div `#sidebarOverlay` closes it on tap.

## Domain vocabulary

| Term | Meaning |
|---|---|
| Liberación | Quality-control release of a road section |
| Solicitud | Individual material request record |
| Hito | Milestone/station code (e.g. M11A, N160) |
| Abscisa | Chainage position along the road (metres) |
| Tramo (TR3 / TR4) | Road segment 3 or 4 |
| Cumplimiento | Compliance percentage (executed ÷ programmed) |
| Granulares | Aggregate materials (subbase + base) |

Status values for `estado`: `liberado`, `pendiente`, `rechazado`.
