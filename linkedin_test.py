import os
import requests
import json
import re
from dotenv import load_dotenv

# 1. Cargar la API Key de forma segura desde tu archivo .env
load_dotenv()
api_key = os.getenv("RAPIDAPI_KEY")


def obtener_detalle_empleo(job_id):
    # La URL ahora apunta al endpoint de detalle de un trabajo específico
    url = f"https://linkedin-jobs.p.rapidapi.com/job/{job_id}"

    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": "linkedin-jobs.p.rapidapi.com",
        "x-rapidapi-key": api_key  # Usamos la variable, NO la llave en duro
    }

    print(f"Consultando los detalles del empleo ID: {job_id}...")

    # Nota que aquí usamos requests.get(), no .post()
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        datos = response.json()
        print("\n✅ Extracción exitosa. Detalles del puesto:\n")

        # 1. Extraemos los campos principales de forma segura
        titulo = datos.get("job_title", "Sin título")
        empresa = datos.get("company", {}).get("name", "Empresa oculta")
        modalidad = datos.get("job_type", "No especificado")

        # 2. Extraemos y limpiamos la descripción (quitamos el HTML)
        descripcion_raw = datos.get("description", "")

        # Reemplazamos los saltos de línea HTML por saltos reales
        desc_limpia = descripcion_raw.replace("<br/>", "\n")
        # Usamos una expresión regular simple para quitar cualquier otra etiqueta (como <strong>)
        desc_limpia = re.sub(r'<[^>]+>', '', desc_limpia)

        print(f"📌 Puesto: {titulo}")
        print(f"🏢 Empresa: {empresa} | 🕒 Modalidad: {modalidad}\n")
        print("📄 Descripción del Cargo:")
        print("-" * 40)
        print(desc_limpia)
        print("-" * 40)

        return datos


if __name__ == "__main__":
    if not api_key:
        print("⚠️ Error: No se encontró RAPIDAPI_KEY en el archivo .env.")
    else:
        # Probamos con el ID exacto que venía en tu comando cURL
        id_prueba = "4403527236"
        detalle = obtener_detalle_empleo(id_prueba)

        # Si quisieras extraer algo en particular del detalle:
        # if detalle:
        #     print("\nDescripción extraída:", detalle.get('description', 'No hay descripción'))