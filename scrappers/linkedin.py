"""
scrapers/linkedin.py
Scraper de ofertas laborales desde LinkedIn Jobs.

LinkedIn requiere sesión autenticada para ver resultados completos.
Las credenciales se leen desde variables de entorno:
    LINKEDIN_EMAIL
    LINKEDIN_PASSWORD

Dependencias:
    pip install selenium
"""

import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

# ── Configuración ────────────────────────────────────────────────────────────

BASE_URL = "https://www.linkedin.com"
LOGIN_URL = f"{BASE_URL}/login"
JOBS_URL  = f"{BASE_URL}/jobs/search/"

WAIT_TIMEOUT   = 10   # segundos máximos esperando elementos
SCROLL_PAUSE   = 1.5  # pausa entre scrolls para cargar más resultados
MAX_RESULTADOS = 25   # LinkedIn muestra ~25 por página


# ── Driver ───────────────────────────────────────────────────────────────────

def _crear_driver(headless: bool = True) -> webdriver.Chrome:
    """Inicializa Chrome con opciones para scraping."""
    opciones = Options()
    if headless:
        opciones.add_argument("--headless=new")
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--disable-blink-features=AutomationControlled")
    opciones.add_argument("--window-size=1280,800")
    opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
    opciones.add_experimental_option("useAutomationExtension", False)
    opciones.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=opciones)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


# ── Autenticación ────────────────────────────────────────────────────────────

def _login(driver: webdriver.Chrome) -> bool:
    """
    Inicia sesión en LinkedIn.
    Retorna True si el login fue exitoso, False si falló.
    """
    email    = os.getenv("LINKEDIN_EMAIL", "")
    password = os.getenv("LINKEDIN_PASSWORD", "")

    if not email or not password:
        logger.warning(
            "LinkedIn: credenciales no configuradas. "
            "Define LINKEDIN_EMAIL y LINKEDIN_PASSWORD como variables de entorno."
        )
        return False

    try:
        driver.get(LOGIN_URL)
        wait = WebDriverWait(driver, WAIT_TIMEOUT)

        campo_email = wait.until(EC.presence_of_element_located((By.ID, "username")))
        campo_email.send_keys(email)

        campo_pass = driver.find_element(By.ID, "password")
        campo_pass.send_keys(password)
        campo_pass.send_keys(Keys.RETURN)

        # Verificar login exitoso esperando el feed
        wait.until(EC.url_contains("/feed"))
        logger.info("LinkedIn: sesión iniciada correctamente.")
        return True

    except TimeoutException:
        logger.error("LinkedIn: timeout durante el login. ¿Credenciales incorrectas?")
        return False


# ── Scraping ─────────────────────────────────────────────────────────────────

def _construir_url(keywords: list[str], region: str) -> str:
    """Construye la URL de búsqueda de LinkedIn Jobs."""
    from urllib.parse import urlencode
    params = {
        "keywords": " ".join(keywords),
        "location": region,
        "f_TPR": "r86400",  # Publicadas en las últimas 24h
        "sortBy": "DD",     # Más recientes primero
    }
    return f"{JOBS_URL}?{urlencode(params)}"


def _scroll_resultados(driver: webdriver.Chrome) -> None:
    """Hace scroll en el panel de resultados para cargar todas las tarjetas."""
    try:
        panel = driver.find_element(By.CLASS_NAME, "jobs-search-results-list")
        for _ in range(3):
            driver.execute_script("arguments[0].scrollTop += 800", panel)
            time.sleep(SCROLL_PAUSE)
    except NoSuchElementException:
        pass


def _parsear_tarjeta(tarjeta) -> dict | None:
    """Extrae datos de una tarjeta de oferta. Retorna None si falla."""
    try:
        titulo = tarjeta.find_element(
            By.CSS_SELECTOR, ".job-card-list__title"
        ).text.strip()

        empresa = tarjeta.find_element(
            By.CSS_SELECTOR, ".job-card-container__primary-description"
        ).text.strip()

        ubicacion = tarjeta.find_element(
            By.CSS_SELECTOR, ".job-card-container__metadata-item"
        ).text.strip()

        url = tarjeta.find_element(
            By.CSS_SELECTOR, "a.job-card-list__title"
        ).get_attribute("href").split("?")[0]  # limpia parámetros de tracking

        publicado_elem = tarjeta.find_elements(
            By.CSS_SELECTOR, "time"
        )
        publicado = publicado_elem[0].text.strip() if publicado_elem else ""

        # Detectar modalidad desde ubicación o título
        texto = f"{titulo} {ubicacion}".lower()
        if "remoto" in texto or "remote" in texto:
            modalidad = "remoto"
        elif "híbrido" in texto or "hybrid" in texto:
            modalidad = "híbrido"
        else:
            modalidad = "presencial"

        return {
            "titulo":    titulo,
            "empresa":   empresa,
            "ubicacion": ubicacion,
            "modalidad": modalidad,
            "url":       url,
            "publicado": publicado,
            "portal":    "LinkedIn",
        }

    except NoSuchElementException as e:
        logger.debug(f"LinkedIn: tarjeta incompleta, se omite. ({e})")
        return None


# ── Interfaz pública ─────────────────────────────────────────────────────────

def buscar(keywords: list[str], region: str = "Chile") -> list[dict]:
    """
    Busca ofertas laborales en LinkedIn Jobs.

    Args:
        keywords: Lista de términos de búsqueda.
        region:   Ubicación a filtrar (por defecto "Chile").

    Returns:
        Lista de ofertas normalizadas. Vacía si hay error o sin credenciales.
    """
    driver = _crear_driver(headless=True)
    ofertas = []

    try:
        autenticado = _login(driver)
        if not autenticado:
            logger.warning("LinkedIn: se continuará sin autenticación (resultados limitados).")

        url = _construir_url(keywords, region)
        driver.get(url)

        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list")))

        _scroll_resultados(driver)

        tarjetas = driver.find_elements(By.CLASS_NAME, "job-card-container")
        logger.info(f"LinkedIn: {len(tarjetas)} tarjetas encontradas.")

        for tarjeta in tarjetas[:MAX_RESULTADOS]:
            oferta = _parsear_tarjeta(tarjeta)
            if oferta:
                ofertas.append(oferta)

    except TimeoutException:
        logger.error("LinkedIn: timeout al cargar resultados. ¿Cambió la estructura del sitio?")
    except Exception as e:
        logger.error(f"LinkedIn: error inesperado — {e}")
    finally:
        driver.quit()

    logger.info(f"LinkedIn: {len(ofertas)} ofertas extraídas.")
    return ofertas


# ── Ejecución directa (debug) ─────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s │ %(message)s")
    resultados = buscar(["soporte TI", "helpdesk"], region="Región Metropolitana")
    for o in resultados:
        print(f"[{o['portal']}] {o['titulo']} — {o['empresa']} ({o['modalidad']})")
        print(f"  {o['url']}\n")