import os
import re
import json
from dotenv import load_dotenv
import requests

# 1. Cargar la API Key desde .env
load_dotenv()
api_key = os.getenv("RAPIDAPI_KEY")

RAPIDAPI_HOST = "jsearch.p.rapidapi.com"

HEADERS = {
    "x-rapidapi-host": RAPIDAPI_HOST,
    "x-rapidapi-key": api_key,
}


# ---------------------------------------------------------------------------
# 2. Buscar ofertas por palabras clave y ubicación
# ---------------------------------------------------------------------------

def buscar_empleos(query: str, ubicacion: str = "Chile", pagina: int = 1) -> list[dict]:
    """
    Devuelve una lista de ofertas desde JSearch (Indeed, LinkedIn, Glassdoor y más).
    """
    url = "https://jsearch.p.rapidapi.com/search-v2"

    params = {
        "query": f"{query} in {ubicacion}",
        "page": str(pagina),
        "num_pages": "1",
        "date_posted": "month",     # today | 3days | week | month
        "country": "cl",
        "language": "es",
        "employment_types": "FULLTIME,PARTTIME,CONTRACTOR",
    }

    print(f"🔍 Buscando '{query}' en {ubicacion} (página {pagina})...")
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        print(f"❌ Error en búsqueda: {response.status_code} — {response.text}")
        return []

    datos = response.json()
    hits = datos.get("data", {}).get("jobs", [])
    print(f"   → {len(hits)} ofertas encontradas.\n")
    return hits


# ---------------------------------------------------------------------------
# 3. Obtener el detalle completo de una oferta por su ID
# ---------------------------------------------------------------------------

def obtener_detalle_empleo(job_id: str) -> dict | None:
    """
    Dado un job_id de JSearch, devuelve todos los campos disponibles del puesto.
    """
    url = "https://jsearch.p.rapidapi.com/job-details"

    params = {
        "job_id": job_id,
        "country": "cl",
        "extended_publisher_details": "true",
    }

    print(f"📋 Consultando detalle del empleo ID: {job_id}...")
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        print(f"❌ Error al obtener detalle: {response.status_code} — {response.text}")
        return None

    datos = response.json().get("data", [])
    if not datos:
        print("⚠️  No se encontraron detalles para ese ID.")
        return None

    oferta = datos[0]

    # --- Extraer todos los campos disponibles ---
    titulo        = oferta.get("job_title", "Sin título")
    empresa       = oferta.get("employer_name", "Empresa oculta")
    ciudad        = oferta.get("job_city", "")
    pais          = oferta.get("job_country", "")
    modalidad     = oferta.get("job_employment_type", "No especificado")
    es_remoto     = oferta.get("job_is_remote", False)
    salario_min   = oferta.get("job_min_salary")
    salario_max   = oferta.get("job_max_salary")
    salario_mon   = oferta.get("job_salary_currency", "")
    salario_per   = oferta.get("job_salary_period", "")
    fecha_pub     = oferta.get("job_posted_at_datetime_utc", "Fecha desconocida")
    fecha_exp     = oferta.get("job_offer_expiration_datetime_utc", "No indicada")
    url_oferta    = oferta.get("job_apply_link", "")
    fuente        = oferta.get("job_publisher", "")
    beneficios    = oferta.get("job_benefits", []) or []
    requisitos    = oferta.get("job_required_skills", []) or []
    experiencia   = oferta.get("job_required_experience", {})
    educacion     = oferta.get("job_required_education", {})

    descripcion_raw = oferta.get("job_description", "")
    desc_limpia = re.sub(r"<[^>]+>", "", descripcion_raw).strip()

    # --- Formatear salario ---
    if salario_min and salario_max:
        salario_str = f"{salario_mon} {salario_min:,.0f} – {salario_max:,.0f} / {salario_per}"
    else:
        salario_str = "No indicado"

    # --- Imprimir resultado formateado ---
    print("\n✅ Extracción exitosa\n")
    print(f"📌 Puesto      : {titulo}")
    print(f"🏢 Empresa     : {empresa}")
    print(f"📍 Ubicación   : {ciudad}, {pais}")
    print(f"🌐 Remoto      : {'Sí' if es_remoto else 'No'}")
    print(f"🕒 Modalidad   : {modalidad}")
    print(f"💰 Salario     : {salario_str}")
    print(f"📅 Publicado   : {fecha_pub}")
    print(f"⏳ Expira      : {fecha_exp}")
    print(f"🔗 Postular    : {url_oferta}")
    print(f"📰 Fuente      : {fuente}")

    if requisitos:
        print(f"🛠  Habilidades : {', '.join(requisitos)}")

    if beneficios:
        print(f"🎁 Beneficios  : {', '.join(beneficios)}")

    if experiencia:
        anos = experiencia.get("required_experience_in_months", 0)
        print(f"💼 Experiencia : {anos // 12} años ({anos} meses)")

    if educacion:
        nivel = educacion.get("required_education_level", "")
        if nivel:
            print(f"🎓 Educación   : {nivel}")

    print("\n📄 Descripción del cargo:")
    print("-" * 40)
    print(desc_limpia)
    print("-" * 40)

    return oferta


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
                ciudad = oferta.get("job_city", "")
                print(f"  {i}. [{oferta.get('job_id', '?')}]")
                print(f"     {oferta.get('job_title', '?')} — {oferta.get('employer_name', '?')} ({ciudad})")
            print("=" * 50 + "\n")

            # --- Paso 2: detallar la primera oferta ---
            primer_id = resultados[0].get("job_id")
            if primer_id:
                detalle = obtener_detalle_empleo(primer_id)

                # Guardar respuesta completa en JSON para inspección
                if detalle:
                    os.makedirs("data", exist_ok=True)
                    with open("data/jsearch_detalle.json", "w", encoding="utf-8") as f:
                        json.dump(detalle, f, ensure_ascii=False, indent=2)
                    print("\n💾 Detalle completo guardado en data/jsearch_detalle.json")
        else:
            print("No se encontraron ofertas para los criterios indicados.")