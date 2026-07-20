"""Configuration centrale de l'application."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class Settings:
    """Configuration de l'application avec valeurs par défaut."""

    # Crawler
    START_URL: str = os.getenv("START_URL", "https://www.cnrs.fr/")
    MAX_PAGES: int = int(os.getenv("MAX_PAGES", "20"))
    MAX_DEPTH: int = int(os.getenv("MAX_DEPTH", "3"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "10"))

    # Parallélisation
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))

    # Selenium
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
    CHROME_BINARY_PATH: Optional[str] = os.getenv("CHROME_BINARY_PATH")
    SCROLL_DELAY: float = float(os.getenv("SCROLL_DELAY", "1"))
    RESOURCE_TIMEOUT: int = int(os.getenv("RESOURCE_TIMEOUT", "5"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "outputs/crawler.log")

    # Chemins
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    OUTPUT_DIR: Path = BASE_DIR / "outputs"

    # Ressources à vérifier
    RESOURCE_TYPES: set = {"js", "css", "image"}
    IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"}

    # User Agent
    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # URLs à ignorer
    IGNORED_DOMAINS: set = {
        "google-analytics.com",
        "googletagmanager.com",
        "hcaptcha.com",
        "facebook.net",
        "twitter.com",
        "linkedin.com",
        "youtube.com",
        "vimeo.com",
    }

    # Codes HTTP à ignorer (optionnel)
    IGNORED_STATUS_CODES: set = set()

    # Authentification Basic Auth
    BASIC_AUTH_ENABLED: bool = os.getenv("BASIC_AUTH_ENABLED", "false").lower() == "true"
    BASIC_AUTH_USERNAME: Optional[str] = os.getenv("BASIC_AUTH_USERNAME")
    BASIC_AUTH_PASSWORD: Optional[str] = os.getenv("BASIC_AUTH_PASSWORD")


# Instance globale
settings = Settings()