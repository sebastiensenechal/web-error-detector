"""Configuration du logging pour l'application."""

import logging
import sys
from pathlib import Path

from src.config.settings import settings

# Créer le dossier de sortie si inexistant
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Configuration du logger
def setup_logger() -> logging.Logger:
    """
    Configure et retourne un logger pour l'application.

    Returns:
        Logger configuré
    """
    logger = logging.getLogger("web_error_detector")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler fichier
    log_file = Path(settings.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()