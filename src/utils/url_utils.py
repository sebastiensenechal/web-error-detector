"""Utilitaires pour la gestion des URLs."""

from urllib.parse import urljoin, urlparse, urlunparse

from src.config.settings import settings


def clean_url(url: str) -> str:
    """
    Nettoie une URL en supprimant ancres et paramètres.

    Args:
        url: URL à nettoyer

    Returns:
        URL nettoyée
    """
    parsed = urlparse(url)
    cleaned = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            "",  # params
            "",  # query
            "",  # fragment
        )
    )
    return cleaned


def normalize_url(url: str) -> str:
    """
    Normalise une URL (nettoyage + ajout de slash final si nécessaire).

    Args:
        url: URL à normaliser

    Returns:
        URL normalisée
    """
    cleaned = clean_url(url)
    if not cleaned.endswith("/") and not cleaned.endswith(tuple(settings.IMAGE_EXTENSIONS)):
        cleaned += "/"
    return cleaned


def is_same_domain(base_url: str, url: str) -> bool:
    """
    Vérifie si deux URLs appartiennent au même domaine.

    Args:
        base_url: URL de référence
        url: URL à vérifier

    Returns:
        True si même domaine, False sinon
    """
    base_parsed = urlparse(base_url)
    url_parsed = urlparse(url)
    return base_parsed.netloc == url_parsed.netloc


def is_valid_url(url: str) -> bool:
    """
    Vérifie si une URL est valide et doit être crawlée.

    Args:
        url: URL à vérifier

    Returns:
        True si URL valide, False sinon
    """
    if not url or url.startswith("#"):
        return False

    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return False

    # Ignorer les domaines tiers
    if any(domain in parsed.netloc for domain in settings.IGNORED_DOMAINS):
        return False

    # Ignorer les fichiers non-HTML
    if any(url.endswith(ext) for ext in [".pdf", ".doc", ".docx", ".xls", ".xlsx"]):
        return False

    return True