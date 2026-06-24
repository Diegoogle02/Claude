"""
Extractor de datos — Plataforma Webu / Ariguaní
Descarga Solicitudes/Liberaciones, Avance de Obra e Inventario a Excel.
"""

import sys
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
from getpass import getpass

BASE_URL  = "https://www.ariguani.com.co/Webu"
USUARIO   = "d.moreira"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    ),
    "Accept-Language": "es-CO,es;q=0.9",
}


# ── 1. LOGIN ────────────────────────────────────────────────────────────────

def login(session: requests.Session, contrasena: str) -> bool:
    """Autentica la sesión. Retorna True si el login fue exitoso."""

    # GET para capturar tokens CSRF / campos ocultos
    get_resp = session.get(f"{BASE_URL}/login", headers=HEADERS)
    soup = BeautifulSoup(get_resp.text, "html.parser")

    payload: dict = {}

    # Extrae campos ocultos del formulario (CSRF, etc.)
    form = soup.find("form")
    if form:
        for inp in form.find_all("input", {"type": "hidden"}):
            name = inp.get("name")
            if name:
                payload[name] = inp.get("value", "")

        # Detecta nombres reales de los campos de usuario/contraseña
        for inp in form.find_all("input"):
            name  = inp.get("name", "")
            nlow  = name.lower()
            if any(k in nlow for k in ("user", "usuario", "login", "email")):
                payload[name] = USUARIO
            elif any(k in nlow for k in ("pass", "contra", "pwd", "clave")):
                payload[name] = contrasena

    # Fallback si el form no tiene campos identificables
    if not any(k for k in payload if any(x in k.lower() for x in ("user", "usuario"))):
        payload.update({"usuario": USUARIO, "contrasena": contrasena})

    post_resp = session.post(
        f"{BASE_URL}/login",
        data=payload,
        headers={**HEADERS, "Referer": f"{BASE_URL}/login",
                 "Content-Type": "application/x-www-form-urlencoded"},
        allow_redirects=True,
    )

    # Si sigue en /login probablemente falló
    if "/login" in post_resp.url:
        print(f"  URL post-login: {post_resp.url}")
        return False

    print(f"  ✅ Sesión activa — redirigido a: {post_resp.url}")
    return True


# ── 2. EXTRACCIÓN DE PÁGINA ─────────────────────────────────────────────────

def fetch_page(session: requests.Session, path: str) -> tuple[str, BeautifulSoup]:
    url  = f"{BASE_URL}/{path}"
    resp = session.get(url, headers={**HEADERS, "Referer": BASE_URL})
    print(f"  GET {url}  →  HTTP {resp.status_code}")
    return resp.text, BeautifulSoup(resp.text, "html.parser")


def extract_tables(soup: BeautifulSoup) -> list[pd.DataFrame]:
    """Extrae todas las <table> del HTML como DataFrames."""
    tables = soup.find_all("table")
    dfs = []
    for i, tbl in enumerate(tables):
        try:
            df = pd.read_html(str(tbl))[0]
            dfs.append(df)
            print(f"    Tabla {i+1}: {len(df)} filas × {len(df.columns)} columnas")
        except Exception:
            pass
    return dfs


def extract_api_json(session: requests.Session, soup: BeautifulSoup) -> list[dict]:
    """
    Intenta detectar endpoints JSON embebidos en scripts de la página
    y llamarlos directamente.
    """
    results = []
    for script in soup.find_all("script"):
        text = script.string or ""
        # Busca patrones tipo fetch('/api/...') o axios.get('/Webu/api/...')
        import re
        urls = re.findall(r"""(?:fetch|axios\.get|\.get)\s*\(\s*['"]([^'"]+)['"]""", text)
        for rel in urls:
            api_url = rel if rel.startswith("http") else f"https://www.ariguani.com.co{rel}"
            try:
                r = session.get(api_url, headers=HEADERS, timeout=10)
                if "application/json" in r.headers.get("Content-Type", ""):
                    results.append({"url": api_url, "data": r.json()})
                    print(f"    API detectada: {api_url}")
            except Exception:
                pass
    return results


def save_excel(dfs: list[pd.DataFrame], filename: str) -> None:
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        for i, df in enumerate(dfs):
            sheet = f"Hoja_{i+1}" if len(dfs) > 1 else "Datos"
            df.to_excel(writer, sheet_name=sheet, index=False)
    print(f"    💾 Guardado: {filename}")


def save_json(data: list[dict], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"    💾 Guardado: {filename}")


def save_raw_html(html: str, filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"    ⚠️  Sin datos estructurados. HTML guardado: {filename}")


# ── 3. MÓDULOS A EXTRAER ─────────────────────────────────────────────────────

# (path relativo a /Webu/, nombre de archivo de salida)
# Ajusta los paths si la URL real es diferente
MODULES = [
    ("soliliberacion",  "solicitudes_liberaciones.xlsx"),
    ("avanceobra",      "avance_obra.xlsx"),
    ("inventario",      "inventario_materiales.xlsx"),
]


# ── 4. MAIN ──────────────────────────────────────────────────────────────────

def main() -> None:
    contrasena = getpass("Contraseña Webu (no se muestra al escribir): ")

    session = requests.Session()

    print("\n── Iniciando sesión ──")
    if not login(session, contrasena):
        print("❌ Login fallido. Verifica usuario/contraseña.")
        sys.exit(1)

    for path, output in MODULES:
        print(f"\n── Extrayendo: /{path} ──")
        html, soup = fetch_page(session, path)

        # Intenta tablas HTML primero
        dfs = extract_tables(soup)
        if dfs:
            save_excel(dfs, output)
            continue

        # Intenta endpoints JSON detectados en la página
        api_data = extract_api_json(session, soup)
        if api_data:
            save_json(api_data, output.replace(".xlsx", ".json"))
            continue

        # Guarda HTML crudo para inspección manual
        save_raw_html(html, output.replace(".xlsx", ".html"))

    print("\n✅ Extracción finalizada. Revisa los archivos generados.")


if __name__ == "__main__":
    main()
