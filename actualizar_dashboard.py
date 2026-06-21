"""
actualizar_dashboard.py
-----------------------
Procesa los 5 archivos Excel de Webu y actualiza design-system/index.html
con los datos reales de TR3 y TR4.

Uso:
    python actualizar_dashboard.py

Los archivos Excel deben estar en la misma carpeta que este script
(o en la ruta configurada en RUTAS abajo).
"""

import re
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

try:
    import pandas as pd
except ImportError:
    sys.exit("Instala dependencias: pip install pandas openpyxl")

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────

BASE_DIR   = Path(__file__).parent
HTML_PATH  = BASE_DIR / "design-system" / "index.html"

# Ajusta estos nombres si descargas los Excel con otro nombre
RUTAS = {
    "lib":       BASE_DIR / "Liberacion*.xlsx",
    "mat_sol":   BASE_DIR / "Reporte_solicitudes_Materiales*.xlsx",
    "asfalt_sol":BASE_DIR / "Reporte_solicitudes_Asfalto*.xlsx",
    "trans_mat": BASE_DIR / "Reporte_transportes_Materiales*.xlsx",
    "trans_asf": BASE_DIR / "Reporte_transportes_Asfalto*.xlsx",
}

TRAMOS = ["3", "4"]

FAMILIAS_MAT = {
    "Granulares": ["Subbase", "Base", "Base Reciclada C.", "Clasificado"],
    "Tierras":    ["Terraplen - M. corte", "Tierra Negra", "CRUDO",
                   "Material Existente", "Corona"],
    "Fresado":    ["Fresado", "Recebo", "RAP"],
}


# ── HELPERS ───────────────────────────────────────────────────────────────────

def glob_one(pattern: Path) -> Path | None:
    matches = sorted(BASE_DIR.glob(pattern.name), reverse=True)
    return matches[0] if matches else None


def _safe_int(val) -> int:
    try:
        return int(str(val).replace("+", ""))
    except Exception:
        return 0


# ── CARGA DE DATOS ────────────────────────────────────────────────────────────

def cargar_liberaciones(path: Path) -> pd.DataFrame:
    raw = pd.read_excel(path, skiprows=1)
    cols = raw.iloc[0].tolist()
    df = raw.iloc[1:].copy()
    df.columns = cols
    df = df.dropna(subset=["Solicitud"]).copy()
    df["Tramo"] = df["Tramo"].astype(str).str.strip()
    return df[df["Tramo"].isin(TRAMOS)].copy()


def cargar_solicitudes(path: Path, col_destino: str = "Destino") -> pd.DataFrame:
    df = pd.read_excel(path)
    df["_tramo"] = df[col_destino].str.extract(r"TRAMO\s+(\d+)", expand=False)
    return df[df["_tramo"].isin(TRAMOS)].copy()


def cargar_transportes(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path)
    df["FRENTE"] = pd.to_numeric(df["FRENTE"], errors="coerce")
    return df[df["FRENTE"].isin([3.0, 4.0])].copy()


# ── CÁLCULO DE KPIs ──────────────────────────────────────────────────────────

def calcular_kpis(lib, mat_sol, asf_sol, trans_mat):
    total_sol   = len(mat_sol) + len(asf_sol)
    m3_prog     = mat_sol["Cantidad solicitada"].sum()
    m3_ejec     = mat_sol["Cantidad enviada"].sum()
    cumpl       = (m3_ejec / m3_prog * 100) if m3_prog else 0
    brecha      = m3_prog - m3_ejec
    total_lib   = len(lib)
    pendientes  = int((lib["Estado Firmas"] == "Pendiente").sum())

    tr3_lib = int((lib["Tramo"] == "3").sum())
    tr4_lib = int((lib["Tramo"] == "4").sum())
    tr3_sol = int((mat_sol["_tramo"] == "3").sum()) + int((asf_sol["_tramo"] == "3").sum())
    tr4_sol = int((mat_sol["_tramo"] == "4").sum()) + int((asf_sol["_tramo"] == "4").sum())

    return {
        "total_sol":  total_sol,
        "tr3_sol":    tr3_sol,
        "tr4_sol":    tr4_sol,
        "m3_prog":    m3_prog,
        "m3_ejec":    m3_ejec,
        "cumpl":      cumpl,
        "brecha":     brecha,
        "total_lib":  total_lib,
        "tr3_lib":    tr3_lib,
        "tr4_lib":    tr4_lib,
        "pendientes": pendientes,
    }


def calcular_familias(mat_sol):
    result = {}
    for nombre, materiales in FAMILIAS_MAT.items():
        sub = mat_sol[mat_sol["Formula / Material"].isin(materiales)]
        sol = sub["Cantidad solicitada"].sum()
        env = sub["Cantidad enviada"].sum()
        pct = (env / sol * 100) if sol > 0 else 0
        result[nombre] = {"sol": sol, "env": env, "pct": round(pct, 1)}
    return result


def calcular_charts(mat_sol, trans_mat):
    # Barras: programado vs ejecutado por mes
    tmp = mat_sol.copy()
    tmp["_fecha"] = pd.to_datetime(
        tmp["Fecha de solicitud"].astype(str).str[:10], errors="coerce"
    )
    tmp["_mes"] = tmp["_fecha"].dt.strftime("%b")
    monthly = tmp.groupby("_mes")[["Cantidad solicitada", "Cantidad enviada"]].sum()

    meses_es = {"Jan": "Ene", "Feb": "Feb", "Mar": "Mar", "Apr": "Abr",
                "May": "May", "Jun": "Jun", "Jul": "Jul", "Aug": "Ago",
                "Sep": "Sep", "Oct": "Oct", "Nov": "Nov", "Dec": "Dic"}
    meses = [meses_es.get(m, m) for m in monthly.index.tolist()]
    prog  = monthly["Cantidad solicitada"].round(0).astype(int).tolist()
    real  = monthly["Cantidad enviada"].round(0).astype(int).tolist()

    # Doughnut: distribución por material (viajes)
    dist  = trans_mat["MATERIAL"].value_counts().head(6)
    total = dist.sum()
    donut_labels = dist.index.tolist()
    donut_data   = [round(v / total * 100, 1) for v in dist.values]

    return meses, prog, real, donut_labels, donut_data


def top10_liberaciones(lib):
    lib_s = lib.sort_values("Fecha de liberación", ascending=False)
    cols = ["Solicitud", "Fecha de liberación", "Tramo", "Hito",
            "Material / Formula", "Capa", "Abscisa Inicial", "Abscisa Final",
            "Estado Firmas"]
    rows = lib_s[cols].head(10).to_dict("records")

    estado_map = {
        "Liberado":            "liberado",
        "Pendiente":           "pendiente",
        "Solicitud Rechazada": "rechazado",
    }

    js_rows = []
    for r in rows:
        sol    = int(r["Solicitud"])
        fecha  = str(r["Fecha de liberación"])[:10].replace("-", "/")
        if len(fecha) == 10 and fecha[4] == "/":
            fecha = f"{fecha[8:]}/{fecha[5:7]}/{fecha[:4]}"
        tramo  = str(r["Tramo"]).strip()
        hito   = str(r["Hito"]).strip()
        mat    = str(r["Material / Formula"]).strip()
        mat    = "—" if mat in ("nan", "None", "") else mat
        capa   = str(r["Capa"]).strip()
        abs_i  = _safe_int(r["Abscisa Inicial"])
        abs_f  = _safe_int(r["Abscisa Final"])
        ml     = abs(abs_f - abs_i)
        estado = estado_map.get(str(r["Estado Firmas"]).strip(), "pendiente")
        js_rows.append(
            f"  {{ sol: {sol}, fecha: '{fecha}', tramo: '{tramo}', "
            f"hito: '{hito}', material: '{mat}', capa: '{capa}', "
            f"ml: {ml}, estado: '{estado}' }},"
        )
    return js_rows


# ── ACTUALIZACIÓN DEL HTML ────────────────────────────────────────────────────

def reemplazar(html: str, patron: str, nuevo: str) -> str:
    return re.sub(patron, nuevo, html, flags=re.DOTALL)


def actualizar_html(kpis, familias, charts, lib_rows, mes_label, total_trans):
    html = HTML_PATH.read_text(encoding="utf-8")

    meses, prog, real, donut_labels, donut_data = charts

    # Subtítulo página
    html = reemplazar(
        html,
        r'(<p class="page-subtitle">)[^<]*(</p>)',
        f'\\g<1>Tramos 3 y 4 · {mes_label} · {kpis["total_sol"]} solicitudes · '
        f'{kpis["total_lib"]} liberaciones · {total_trans:,} transportes\\g<2>',
    )

    # Navbar breadcrumb
    html = reemplazar(
        html,
        r'(<span class="current">)[^<]*(</span>)',
        f'\\g<1>Dashboard · {mes_label} · TR3 &amp; TR4\\g<2>',
    )

    # Sidebar counts
    html = re.sub(
        r'(Liberaciones\s*<span class="nav-count">)[^<]*(</span>)',
        f'\\g<1>{kpis["total_lib"]}\\g<2>', html,
    )
    html = re.sub(
        r'(Solicitudes\s*<span class="nav-count">)[^<]*(</span>)',
        f'\\g<1>{kpis["total_sol"]}\\g<2>', html,
    )
    html = re.sub(
        r'(Pendientes\s*<span class="nav-count"[^>]*>)[^<]*(</span>)',
        f'\\g<1>{kpis["pendientes"]}\\g<2>', html,
    )

    # KPI cards (por posición en el HTML, más seguro con patrones únicos)
    def kpi_val(old_val, new_val):
        return (
            f'<div class="kpi-value">{old_val}</div>',
            f'<div class="kpi-value">{new_val}</div>',
        )

    m3p_fmt  = f'{kpis["m3_prog"]/1000:.1f}K'
    m3e_fmt  = f'{kpis["m3_ejec"]/1000:.1f}K'
    cumpl_s  = f'{kpis["cumpl"]:.1f}%'
    brecha_s = f'{kpis["brecha"]:,.0f} m³'.replace(",", ".")

    replacements = [
        # Total solicitudes
        (r'(<div class="kpi-label">Total Solicitudes</div>\s*<div class="kpi-value">)[^<]*(</div>\s*<div class="kpi-sub">)[^<]*(</div>)',
         f'\\g<1>{kpis["total_sol"]}\\g<2>TR3: {kpis["tr3_sol"]} · TR4: {kpis["tr4_sol"]}\\g<3>'),
        # m³ Programado
        (r'(<div class="kpi-label">m³ Programado</div>\s*<div class="kpi-value">)[^<]*(</div>\s*<div class="kpi-sub">)[^<]*(</div>)',
         f'\\g<1>{m3p_fmt}\\g<2>{kpis["m3_prog"]:,.0f} m³ en plan\\g<3>'),
        # m³ Ejecutado
        (r'(<div class="kpi-label">m³ Ejecutado</div>\s*<div class="kpi-value">)[^<]*(</div>\s*<div class="kpi-sub">)[^<]*(</div>)',
         f'\\g<1>{m3e_fmt}\\g<2>{kpis["m3_ejec"]:,.0f} m³ reales\\g<3>'),
        # Cumplimiento
        (r'(<div class="kpi-label">Cumplimiento Global</div>\s*<div class="kpi-value">)[^<]*(</div>\s*<div class="kpi-sub">)[^<]*(</div>)',
         f'\\g<1>{cumpl_s}\\g<2>Brecha: {brecha_s}\\g<3>'),
        # Liberaciones
        (r'(<div class="kpi-label">Liberaciones</div>\s*<div class="kpi-value">)[^<]*(</div>\s*<div class="kpi-sub">)[^<]*(</div>)',
         f'\\g<1>{kpis["total_lib"]}\\g<2>TR3: {kpis["tr3_lib"]} · TR4: {kpis["tr4_lib"]}\\g<3>'),
        # Pendientes
        (r'(<div class="kpi-label">Pendientes</div>\s*<div class="kpi-value">)[^<]*(</div>)',
         f'\\g<1>{kpis["pendientes"]}\\g<2>'),
    ]
    for patron, nuevo in replacements:
        html = reemplazar(html, patron, nuevo)

    # Tabla footer count
    html = re.sub(
        r'Mostrando \d+ de \d+ liberaciones[^<]*',
        f'Mostrando 10 de {kpis["total_lib"]} liberaciones · '
        f'TR3: {kpis["tr3_lib"]} · TR4: {kpis["tr4_lib"]}',
        html,
    )

    # JS: array liberaciones
    rows_js = "\n".join(lib_rows)
    html = reemplazar(
        html,
        r'/\* ---- Datos.*?---- \*/\nconst liberaciones = \[.*?\];',
        f'/* ---- Datos reales Webu · {mes_label} · TR3 & TR4 ---- */\n'
        f'const liberaciones = [\n{rows_js}\n];',
    )

    # JS: chart barras
    meses_js  = str(meses).replace("'", "'")
    prog_js   = str(prog)
    real_js   = str(real)
    html = reemplazar(
        html,
        r'(function initCharts\(\) \{.*?const meses = )\[.*?\](;.*?const prog\s*= )\[.*?\](;.*?const real\s*= )\[.*?\](;)',
        f'\\g<1>{meses_js}\\g<2>{prog_js}\\g<3>{real_js}\\g<4>',
    )

    # JS: doughnut labels + data
    donut_labels_js = str(donut_labels)
    donut_data_js   = str(donut_data)
    html = reemplazar(
        html,
        r"(labels: \[')([^']+(?:', '[^']+)*)('\],\s*datasets: \[\{[\s\S]*?data: )\[[^\]]+\]",
        f"labels: {donut_labels_js},\n      datasets: [{{\\n        data: {donut_data_js}",
    )

    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"✅ {HTML_PATH} actualizado.")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("Buscando archivos Excel...")

    # Carga de archivos (acepta tanto rutas fijas como glob)
    def find(key):
        p = RUTAS[key]
        if p.exists():
            return p
        found = glob_one(p)
        if found:
            return found
        sys.exit(f"❌ No se encontró el archivo para '{key}': {p}")

    lib       = cargar_liberaciones(find("lib"))
    mat_sol   = cargar_solicitudes(find("mat_sol"))
    asf_sol   = cargar_solicitudes(find("asfalt_sol"))
    trans_mat = cargar_transportes(find("trans_mat"))
    trans_asf = cargar_transportes(find("trans_asf"))

    print(f"  Liberaciones TR3/TR4:       {len(lib)}")
    print(f"  Solicitudes materiales TR3/TR4: {len(mat_sol)}")
    print(f"  Solicitudes asfalto TR3/TR4:    {len(asf_sol)}")
    print(f"  Transportes materiales TR3/TR4: {len(trans_mat)}")
    print(f"  Transportes asfalto TR3/TR4:    {len(trans_asf)}")

    kpis      = calcular_kpis(lib, mat_sol, asf_sol, trans_mat)
    familias  = calcular_familias(mat_sol)
    charts    = calcular_charts(mat_sol, trans_mat)
    lib_rows  = top10_liberaciones(lib)

    import datetime
    mes_label = datetime.date.today().strftime("%b %Y")

    total_trans = len(trans_mat) + len(trans_asf)

    print("\n── KPIs calculados ──")
    print(f"  Solicitudes totales:  {kpis['total_sol']}")
    print(f"  m³ Programado:        {kpis['m3_prog']:,.0f}")
    print(f"  m³ Ejecutado:         {kpis['m3_ejec']:,.0f}")
    print(f"  Cumplimiento:         {kpis['cumpl']:.1f}%")
    print(f"  Liberaciones:         {kpis['total_lib']}")
    print(f"  Pendientes:           {kpis['pendientes']}")

    print("\n── Familias de material ──")
    for nombre, v in familias.items():
        print(f"  {nombre}: {v['env']:,.0f} / {v['sol']:,.0f} m³ = {v['pct']}%")

    print("\nActualizando dashboard...")
    actualizar_html(kpis, familias, charts, lib_rows, mes_label, total_trans)

    print("\n✅ Listo. Abre design-system/index.html en tu navegador.")


if __name__ == "__main__":
    main()
