"""
main.py
Punto de entrada de Trabaja Menos.

Uso:
    python main.py                    # ejecuta verificación de conexión
    python main.py --buscar           # lanza búsqueda completa (próximamente)
"""

import sys
import logging
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s │ %(message)s"
)
logger = logging.getLogger(__name__)

# ── Portales a verificar ──────────────────────────────────────────────────────

PORTALES = [
    {
        "nombre": "GetOnBoard",
        "url":    "https://www.getonbrd.com",
    },
    {
        "nombre": "Computrabajo",
        "url":    "https://www.computrabajo.cl",
    },
    {
        "nombre": "Laborum",
        "url":    "https://www.laborum.cl",
    },
    {
        "nombre": "LinkedIn",
        "url":    "https://www.linkedin.com",
    },
]

TIMEOUT = 8  # segundos

# ── Verificación de conexión ──────────────────────────────────────────────────

def verificar_conexion() -> dict[str, bool]:
    """
    Intenta conectarse a cada portal y reporta el resultado.
    Retorna un dict { nombre_portal: True/False }.
    """
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    resultados = {}

    print("\n" + "─" * 50)
    print("  🔍  BuscaMenos — Verificación de conexión")
    print("─" * 50)

    for portal in PORTALES:
        nombre = portal["nombre"]
        url    = portal["url"]
        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            # 403 = el servidor responde y bloquea bots → portal accesible
            ok   = resp.status_code < 500
            sufijo = " ⚠️ requiere sesión" if resp.status_code == 403 else ""
            estado = f"✅  {nombre:15s} ({resp.status_code}){sufijo}"
        except requests.exceptions.ConnectionError:
            ok     = False
            estado = f"❌  {nombre:15s} (sin conexión)"
        except requests.exceptions.Timeout:
            ok     = False
            estado = f"⏱️  {nombre:15s} (timeout)"
        except Exception as e:
            ok     = False
            estado = f"⚠️  {nombre:15s} ({e})"

        resultados[nombre] = ok
        print(f"  {estado}")

    print("─" * 50)

    total   = len(resultados)
    activos = sum(resultados.values())
    print(f"  Resultado: {activos}/{total} portales accesibles\n")

    return resultados


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if not args or "--verificar" in args:
        resultados = verificar_conexion()
        if not any(resultados.values()):
            logger.error("No se pudo conectar a ningún portal. Revisa tu conexión a internet.")
            sys.exit(1)

    elif "--buscar" in args:
        print("⚙️  Modo búsqueda aún no implementado. Próximamente en v0.1.")

    else:
        print(f"Argumento desconocido: {args}")
        print("Uso: python main.py [--verificar | --buscar]")
        sys.exit(1)


if __name__ == "__main__":
    main()