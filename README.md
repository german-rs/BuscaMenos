# BuscaMenos
**Buscador de ofertas laborales**
*Porque buscar trabajo no debería ser una actividad de tiempo completo.*

Herramienta en Python que consolida ofertas laborales desde múltiples portales chilenos en un solo lugar, filtrando el ruido para que solo veas lo que realmente te interesa.

---

## 📋 Descripción y motivación

Buscar trabajo en Chile implica revisar manualmente GetOnBoard, Computrabajo, Laborum y LinkedIn por separado, cada uno con su propia interfaz, sus propios filtros y sus propios criterios de relevancia. El resultado: horas perdidas viendo ofertas duplicadas, desactualizadas o irrelevantes.

**BuscaMenos** automatiza ese proceso. Un solo comando extrae, normaliza y presenta las ofertas que coinciden con tu perfil, desde todos los portales a la vez.

La integración con cada portal sigue esta prioridad:
1. **API oficial gratuita** — cuando el portal la ofrece, es el método preferido: más estable, más rápido y más respetuoso con los servidores.
2. **Web scraping** — como alternativa para portales que no disponen de API pública.

---

## 🗂️ Estructura del proyecto

```
buscamenos/
│
├── scrapers/                  # Un módulo por portal
│   ├── __init__.py
│   ├── getonboard.py
│   ├── computrabajo.py
│   ├── laborum.py
│   └── linkedin.py
│
├── core/
│   ├── __init__.py
│   ├── normalizer.py          # Normaliza ofertas a esquema común
│   ├── deduplicator.py        # Elimina duplicados entre portales
│   └── filters.py             # Filtros por cargo, modalidad, ubicación
│
├── output/
│   ├── __init__.py
│   ├── console.py             # Salida en terminal (tabla formateada)
│   └── csv_exporter.py        # Exportación a CSV
│
├── data/                      # Resultados generados (ignorado por git)
│
├── tests/
│
├── config.yaml                # Palabras clave, filtros, portales activos
├── main.py                    # Punto de entrada
├── requirements.txt
└── README.md
```

---

## ⚙️ Instalación y requisitos

**Requisitos del sistema:**
- Python 3.10 o superior
- Google Chrome (para scraping con Selenium, en portales sin API)

**Instalación:**

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/buscamenos.git
cd buscamenos

# Crear entorno virtual
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# Instalar dependencias
pip install -r requirements.txt
```

**Dependencias principales:**

| Librería        | Uso                                          |
|-----------------|----------------------------------------------|
| `requests`      | Consultas a APIs y peticiones HTTP simples   |
| `selenium`      | Scraping de portales con JS dinámico         |
| `beautifulsoup4`| Parseo de HTML                               |
| `pandas`        | Normalización y deduplicación de datos       |
| `rich`          | Salida formateada en terminal                |
| `pyyaml`        | Lectura de configuración                     |

---

## 🚀 Uso

**Configurar búsqueda en `config.yaml`:**

```yaml
keywords:
  - "soporte TI"
  - "mesa de ayuda"
  - "helpdesk"

filters:
  region: "Metropolitana"
  modalidad: "presencial"     # presencial | remoto | híbrido

portales:
  getonboard: true
  computrabajo: true
  laborum: true
  linkedin: true
```

**Ejecutar:**

```bash
python main.py
```

**Exportar resultados a CSV:**

```bash
python main.py --export csv
```

**Ejemplo de salida en terminal:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ Cargo                  │ Empresa        │ Portal       │ Publicado  │
├─────────────────────────────────────────────────────────────────────┤
│ Soporte TI N1          │ Acme S.A.      │ GetOnBoard   │ hoy        │
│ Helpdesk Corporativo   │ Empresa XYZ    │ Computrabajo │ ayer       │
│ Mesa de Ayuda - Remoto │ StartupABC     │ LinkedIn     │ hace 2 días│
└─────────────────────────────────────────────────────────────────────┘
Total: 3 ofertas encontradas (12 duplicados eliminados)
```

---

## 🗺️ Roadmap

### v0.1 — Base funcional
- [ ] Integración con GetOnBoard vía API
- [ ] Scraper de Computrabajo
- [ ] Normalización a esquema común
- [ ] Salida en terminal con `rich`

### v0.2 — Cobertura completa
- [ ] Scraper de Laborum
- [ ] Scraper de LinkedIn
- [ ] Deduplicación entre portales
- [ ] Exportación a CSV

### v0.3 — Usabilidad
- [ ] Configuración por archivo YAML
- [ ] Filtros por modalidad y región
- [ ] Modo `--dry-run` para probar configuración

### v0.4 — Automatización *(tentativo)*
- [ ] Ejecución programada (cron / tarea)
- [ ] Notificación por correo o Telegram al detectar nuevas ofertas
- [ ] Historial de ofertas vistas

---

## ⚠️ Consideraciones legales

Este proyecto es de uso personal. El scraping puede estar limitado por los términos de servicio de cada portal. Úsalo de forma responsable: respeta los tiempos de espera entre peticiones y no sobrecargues los servidores. Siempre que exista una API oficial, se utilizará en su lugar.

---

## 📄 Licencia

MIT