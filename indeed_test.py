import os
import re
import json
from dotenv import load_dotenv
import requests

# 1. Cargar la API Key desde .env
load_dotenv()
api_key = os.getenv("RAPIDAPI_KEY")

RAPIDAPI_HOST = "indeed12.p.rapidapi.com"

HEADERS = {
    "x-rapidapi-host": RAPIDAPI_HOST,
    "x-rapidapi-key": api_key,
}


# ---------------------------------------------------------------------------
# 2. Buscar ofertas por palabras clave y ubicación
# ---------------------------------------------------------------------------

def buscar_empleos(query: str, ubicacion: str = "Chile", pagina: int = 1) -> list[dict]:
    """
    Devuelve una lista de ofertas que coinciden con la búsqueda.
    Cada ítem contiene id, título, empresa, ubicación, fecha y URL.
    """
    url = "https://indeed12.p.rapidapi.com/jobs/search"

    params = {
        "query": query,
        "location": ubicacion,
        "page_id": str(pagina),
        "locality": "cl",       # Filtra resultados a indeed.cl
        "fromage": "7",         # Publicadas en los últimos 7 días
        "radius": "50",         # Km de radio
    }

    print(f"🔍 Buscando '{query}' en {ubicacion} (página {pagina})...")
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        print(f"❌ Error en búsqueda: {response.status_code} — {response.text}")
        return []

    datos = response.json()
    hits = datos.get("hits", [])
    print(f"   → {len(hits)} ofertas encontradas.\n")
    return hits


# ---------------------------------------------------------------------------
# 3. Obtener el detalle completo de una oferta por su ID
# ---------------------------------------------------------------------------

def obtener_detalle_empleo(job_id: str) -> dict | None:
    """
    Dado un job_id de Indeed, devuelve todos los campos disponibles del puesto.
    """
    url = f"https://indeed12.p.rapidapi.com/job/{job_id}"

    print(f"📋 Consultando detalle del empleo ID: {job_id}...")
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"❌ Error al obtener detalle: {response.status_code} — {response.text}")
        return None

    datos = response.json()

    # --- Extraer y limpiar cada campo disponible ---
    titulo        = datos.get("title", "Sin título")
    empresa       = datos.get("company", "Empresa oculta")
    ubicacion     = datos.get("location", {})
    ciudad        = ubicacion.get("city", "")
    pais          = ubicacion.get("countryCode", "")
    modalidad     = datos.get("jobType", "No especificado")
    salario       = datos.get("salarySnippet", {}).get("text", "No indicado")
    fecha_pub     = datos.get("pubDate", "Fecha desconocida")
    url_oferta    = datos.get("link", "")
    beneficios    = datos.get("benefits", [])

    descripcion_raw = datos.get("description", "")
    desc_limpia = descripcion_raw.replace("<br/>", "\n").replace("<br>", "\n")
    desc_limpia = re.sub(r"<[^>]+>", "", desc_limpia).strip()

    # --- Imprimir resultado formateado ---
    print("\n✅ Extracción exitosa\n")
    print(f"📌 Puesto     : {titulo}")
    print(f"🏢 Empresa    : {empresa}")
    print(f"📍 Ubicación  : {ciudad}, {pais}")
    print(f"🕒 Modalidad  : {modalidad}")
    print(f"💰 Salario    : {salario}")
    print(f"📅 Publicado  : {fecha_pub}")
    print(f"🔗 URL        : {url_oferta}")

    if beneficios:
        print(f"🎁 Beneficios : {', '.join(beneficios)}")

    print("\n📄 Descripción del cargo:")
    print("-" * 40)
    print(desc_limpia)
    print("-" * 40)

    return datos


# ---------------------------------------------------------------------------
# 4. Flujo principal: buscar y luego detallar la primera oferta
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not api_key:
        print("⚠️  Error: No se encontró RAPIDAPI_KEY en el archivo .env.")
    else:
        # --- Paso 1: buscar ---
        resultados = buscar_empleos(query="soporte TI", ubicacion="Santiago de Chile")

        if resultados:
            # Mostrar resumen de la búsqueda
            print("=" * 50)
            print("📊 Resumen de ofertas encontradas:\n")
            for i, oferta in enumerate(resultados, 1):
                print(f"  {i}. [{oferta.get('id', '?')}] {oferta.get('title', '?')} — {oferta.get('company', '?')}")
            print("=" * 50 + "\n")

            # --- Paso 2: detallar la primera oferta ---
            primer_id = resultados[0].get("id")
            if primer_id:
                detalle = obtener_detalle_empleo(primer_id)

                # Guardar respuesta completa en JSON para inspección
                if detalle:
                    with open("data/indeed_detalle.json", "w", encoding="utf-8") as f:
                        json.dump(detalle, f, ensure_ascii=False, indent=2)
                    print("\n💾 Detalle completo guardado en data/indeed_detalle.json")
        else:
            print("No se encontraron ofertas para los criterios indicados.")