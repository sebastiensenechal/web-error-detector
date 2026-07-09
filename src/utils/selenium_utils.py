"""Utilitaires pour Selenium."""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from src.config.settings import settings
from src.utils.logger import logger


def get_driver() -> webdriver.Chrome:
    """
    Crée et configure un driver Selenium Chrome.

    Returns:
        Instance de WebDriver
    """
    options = Options()

    # Configuration headless
    if settings.HEADLESS:
        options.add_argument("--headless")

    # Autres options
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"--user-agent={settings.USER_AGENT}")

    # Chemin binaire Chrome si spécifié
    if settings.CHROME_BINARY_PATH:
        options.binary_location = settings.CHROME_BINARY_PATH

    # Options pour réduire les logs
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # Désactiver les extensions
    options.add_argument("--disable-extensions")

    # Accepter les certificats SSL invalides (optionnel)
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--allow-running-insecure-content")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        logger.info("Selenium WebDriver initialized successfully")
        return driver

    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        raise