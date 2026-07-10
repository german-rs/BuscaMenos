"""
EJEMPLO DIDÁCTICO: Web Scraping con BeautifulSoup
Sitio: GetOnBoard (getonbrd.cl)

¿Qué hace este script?
1. Hace una petición HTTP a la página de búsqueda de GetOnBoard
2. Parsea el HTML para encontrar las tarjetas de empleo
3. Extrae título, empresa, ubicación y URL de cada oferta
4. Guarda los resultados en un JSON

¿Por qué BeautifulSoup y no Selenium?
- GetOnBoard renderiza bastante contenido en HTML estático
- BeautifulSoup es más simple y rápido para HTML estático
- Selenium se necesita cuando el sitio usa JavaScript para cargar contenido
"""

import time
import json
import os
import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# CONSTANTES
# ---------------------------------------------------------------------------

BASE_URL = "https://www.getonbrd.cl"
HEADERS = {
    # Simulamos ser un navegador real para evitar bloqueos básicos
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-CL,es;q=0.9",
}


# ---------------------------------------------------------------------------
# PASO 1: Obtener el HTML de la página de búsqueda
# ---------------------------------------------------------------------------

def obtener_html(keyword: str) -> str | None:
    """
    Hace una petición GET a GetOnBoard con la keyword dada
    y retorna el HTML crudo como string.
    """
    # GetOnBoard usa el patrón /jobs-KEYWORD para búsquedas
    url = f"{BASE_URL}/jobs-{keyword.replace(' ', '+')}"
    print(f"🌐 Solicitando: {url}")

    response = requests.get(url, headers=HEADERS, timeout=10)

    if response.status_code == 200:
        print(f"   ✅ HTML recibido ({len(response.text):,} caracteres)")
        return response.text
    else:
        print(f"   ❌ Error {response.status_code}")
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
    - modalidad
    - url
    """
    # BeautifulSoup convierte el HTML en un árbol navegable
    soup = BeautifulSoup(html, "html.parser")

    # Buscamos todos los elementos que contienen una oferta
    # Inspeccionando GetOnBoard, las tarjetas están en <a> con clase "gb-results-list__item"
    tarjetas = soup.find_all("a", class_=lambda c: c and "gb-results-list__item" in c)

    print(f"\n🔍 Tarjetas encontradas en el HTML: {len(tarjetas)}")

    ofertas = []

    for tarjeta in tarjetas:
        # --- Título del cargo ---
        titulo_tag = tarjeta.find(class_=lambda c: c and "job-card__title" in c if c else False)
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else "Sin título"

        # --- Empresa ---
        empresa_tag = tarjeta.find(class_=lambda c: c and "job-card__company" in c if c else False)
        empresa = empresa_tag.get_text(strip=True) if empresa_tag else "Empresa oculta"

        # --- Ubicación ---
        ubicacion_tag = tarjeta.find(class_=lambda c: c and "job-card__location" in c if c else False)
        ubicacion = ubicacion_tag.get_text(strip=True) if ubicacion_tag else "No especificada"

        # --- URL de la oferta ---
        url = tarjeta.get("href", "")
        if url and not url.startswith("http"):
            url = BASE_URL + url

        oferta = {
            "titulo": titulo,
            "empresa": empresa,
            "ubicacion": ubicacion,
            "url": url,
        }
        ofertas.append(oferta)

    return ofertas


# ---------------------------------------------------------------------------
# PASO 3: Mostrar resultados y guardar en JSON
# ---------------------------------------------------------------------------

def mostrar_resultados(ofertas: list[dict]) -> None:
    print("\n" + "=" * 55)
    print("📊 OFERTAS ENCONTRADAS EN GETONBOARD\n")

    for i, oferta in enumerate(ofertas, 1):
        print(f"  {i}. {oferta['titulo']}")
        print(f"     🏢 {oferta['empresa']}")
        print(f"     📍 {oferta['ubicacion']}")
        print(f"     🔗 {oferta['url']}")
        print()

    print(f"Total: {len(ofertas)} ofertas")
    print("=" * 55)


def guardar_json(ofertas: list[dict], keyword: str) -> None:
    os.makedirs("data", exist_ok=True)
    filename = f"data/getonboard_{keyword.replace(' ', '_')}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(ofertas, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Resultados guardados en: {filename}")


# ---------------------------------------------------------------------------
# FLUJO PRINCIPAL
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    keyword = "Soporte TI"

    # Paso 1: Obtener HTML
    html = obtener_html(keyword)

    if html:
        # Paso 2: Parsear ofertas
        ofertas = parsear_ofertas(html)

        if ofertas:
            # Paso 3: Mostrar y guardar
            mostrar_resultados(ofertas)
            guardar_json(ofertas, keyword)
        else:
            # Si no encontró tarjetas, el sitio probablemente usa JS dinámico
            # En ese caso habría que usar Selenium
            print("\n⚠️  No se encontraron tarjetas en el HTML.")
            print("   Esto puede significar que GetOnBoard carga las ofertas")
            print("   dinámicamente con JavaScript.")
            print("   → Solución: reemplazar requests por Selenium.")

        # Pausa respetuosa entre peticiones (buena práctica)
        time.sleep(2)