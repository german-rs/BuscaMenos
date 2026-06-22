"""
scrapers/
Módulos de scraping por portal de empleo.

Cada scraper expone una función principal:
    buscar(keywords: list[str], region: str) -> list[dict]

El diccionario retornado por cada scraper sigue el esquema común:
    {
        "titulo":    str,
        "empresa":   str,
        "ubicacion": str,
        "modalidad": str,   # "presencial" | "remoto" | "híbrido" | ""
        "url":       str,
        "publicado": str,   # texto relativo: "hoy", "ayer", "hace 3 días"
        "portal":    str,   # nombre del portal de origen
    }
"""

# from .getonboard import buscar as getonboard
# from .computrabajo import buscar as computrabajo
# from .laborum import buscar as laborum
# from .linkedin import buscar as linkedin

__all__ = ["getonboard", "computrabajo", "laborum", "linkedin"]