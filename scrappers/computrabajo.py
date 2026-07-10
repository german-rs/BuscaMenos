"""
EJEMPLO DIDÁCTICO: Web Scraping con BeautifulSoup
Sitio: Computrabajo Chile (computrabajo.cl)

¿Qué hace este script?
1. Hace una petición HTTP a la página de búsqueda de Computrabajo
2. Parsea el HTML para encontrar las tarjetas de empleo
3. Extrae título, empresa, ubicación, salario y URL de cada oferta
4. Guarda los resultados en un JSON

Diferencia clave con GetOnBoard:
- Computrabajo renderiza las ofertas en HTML estático (sin JS dinámico)
- Eso significa que requests + BeautifulSoup es suficiente, sin necesitar Selenium
"""

import time
import json
import os
import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# CONSTANTES
# ---------------------------------------------------------------------------

BASE_URL = "https://www.computrabajo.cl"
HEADERS = {
    # Simulamos ser un navegador real para evitar bloqueos básicos
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-CL,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ---------------------------------------------------------------------------
# PASO 1: Obtener el HTML de la página de búsqueda
# ---------------------------------------------------------------------------

def obtener_html(keyword: str) -> str | None:
    """
    Hace una petición GET a Computrabajo con la keyword dada
    y retorna el HTML crudo como string.

    Computrabajo usa el patrón:
    /trabajo-de-KEYWORD  →  ej: /trabajo-de-soporte-ti
    """
    slug = keyword.lower().replace(" ", "-")
    url = f"{BASE_URL}/trabajo-de-{slug}"
    print(f"🌐 Solicitando: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"   → Status: {response.status_code}")

        if response.status_code == 200:
            print(f"   ✅ HTML recibido ({len(response.text):,} caracteres)")
            return response.text
        elif response.status_code == 403:
            print("   ⚠️  Error 403: El servidor bloqueó la petición.")
            print("      → Solución: usar Selenium para simular navegador real.")
            return None
        else:
            print(f"   ❌ Error inesperado: {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print("   ❌ Timeout: el servidor tardó demasiado en responder.")
        return None
    except requests.exceptions.ConnectionError:
        print("   ❌ Error de conexión.")
        return None


# ---------------------------------------------------------------------------
# PASO 2: Parsear el HTML y extraer las ofertas
# ---------------------------------------------------------------------------

def parsear_ofertas(html: str) -> list[dict]:
    """
    Recibe el HTML crudo y devuelve una lista de ofertas con:
    - titulo
    - empresa
    - ubicacion
    - salario (si está disponible)
    - fecha
    - url
    """
    soup = BeautifulSoup(html, "html.parser")

    # Computrabajo envuelve cada oferta en un <article> con clase "box_offer"
    tarjetas = soup.find_all("article", class_=lambda c: c and "box_offer" in c)

    # Alternativa si lo anterior no funciona: buscar por atributo data
    if not tarjetas:
        tarjetas = soup.find_all("article", attrs={"data-id": True})

    print(f"\n🔍 Tarjetas encontradas en el HTML: {len(tarjetas)}")

    ofertas = []

    for tarjeta in tarjetas:
        # --- Título del cargo ---
        titulo_tag = tarjeta.find("h2")
        if not titulo_tag:
            titulo_tag = tarjeta.find(class_=lambda c: c and "js-o-link" in c if c else False)
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else "Sin título"

        # --- URL de la oferta ---
        link_tag = tarjeta.find("a", class_=lambda c: c and "js-o-link" in c if c else False)
        if not link_tag:
            link_tag = tarjeta.find("a", href=True)
        url = link_tag["href"] if link_tag else ""
        if url and not url.startswith("http"):
            url = BASE_URL + url

        # --- Empresa ---
        empresa_tag = tarjeta.find(class_=lambda c: c and "fc_base" in c if c else False)
        empresa = empresa_tag.get_text(strip=True) if empresa_tag else "Empresa oculta"

        # --- Ubicación ---
        ubicacion_tag = tarjeta.find("p", class_=lambda c: c and "fs16" in c if c else False)
        if not ubicacion_tag:
            ubicacion_tag = tarjeta.find(attrs={"itemprop": "addressLocality"})
        ubicacion = ubicacion_tag.get_text(strip=True) if ubicacion_tag else "No especificada"

        # --- Salario (no siempre está disponible) ---
        salario_tag = tarjeta.find(class_=lambda c: c and "salary" in c if c else False)
        salario = salario_tag.get_text(strip=True) if salario_tag else "No indicado"

        # --- Fecha de publicación ---
        fecha_tag = tarjeta.find("time")
        fecha = fecha_tag.get("datetime", fecha_tag.get_text(strip=True)) if fecha_tag else "No indicada"

        oferta = {
            "titulo": titulo,
            "empresa": empresa,
            "ubicacion": ubicacion,
            "salario": salario,
            "fecha": fecha,
            "url": url,
            "fuente": "Computrabajo",
        }
        ofertas.append(oferta)

    return ofertas


# ---------------------------------------------------------------------------
# PASO 3: Mostrar resultados y guardar en JSON
# ---------------------------------------------------------------------------

def mostrar_resultados(ofertas: list[dict]) -> None:
    print("\n" + "=" * 55)
    print("📊 OFERTAS ENCONTRADAS EN COMPUTRABAJO\n")

    for i, oferta in enumerate(ofertas, 1):
        print(f"  {i}. {oferta['titulo']}")
        print(f"     🏢 {oferta['empresa']}")
        print(f"     📍 {oferta['ubicacion']}")
        print(f"     💰 {oferta['salario']}")
        print(f"     📅 {oferta['fecha']}")
        print(f"     🔗 {oferta['url']}")
        print()

    print(f"Total: {len(ofertas)} ofertas")
    print("=" * 55)


def guardar_json(ofertas: list[dict], keyword: str) -> None:
    os.makedirs("data", exist_ok=True)
    filename = f"data/computrabajo_{keyword.replace(' ', '_')}.json"
    os.makedirs("data", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(ofertas, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Resultados guardados en: {filename}")


# ---------------------------------------------------------------------------
# FLUJO PRINCIPAL
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    keyword = "soporte ti"

    # Paso 1: Obtener HTML
    html = obtener_html(keyword)

    if html:
        # Construir ruta absoluta a la carpeta data en la raíz del proyecto
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        DATA_DIR = os.path.join(BASE_DIR, "data")
        os.makedirs(DATA_DIR, exist_ok=True)

        with open(os.path.join(DATA_DIR, "computrabajo_raw.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print("   💾 HTML crudo guardado en data/computrabajo_raw.html")
        # Paso 2: Parsear ofertas
        ofertas = parsear_ofertas(html)

        if ofertas:
            mostrar_resultados(ofertas)
            guardar_json(ofertas, keyword)
        else:
            print("\n⚠️  No se encontraron tarjetas en el HTML.")
            print("   Revisa data/computrabajo_raw.html en el navegador")
            print("   para ver qué clases CSS usa Computrabajo actualmente.")

        # Pausa respetuosa entre peticiones
        time.sleep(2)