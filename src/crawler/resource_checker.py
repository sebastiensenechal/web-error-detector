"""Module de vérification des ressources (JS, CSS, images)."""
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

from selenium.webdriver.remote.webdriver import WebDriver

from src.config.settings import settings
from src.utils.logger import logger

class ResourceChecker:
    """Vérificateur de ressources avec parallélisme et gestion des URLs relatives."""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        })

    def _make_absolute_url(self, base_url: str, url: str) -> Optional[str]:
        """Convertit une URL relative en absolue si nécessaire."""
        if not url or url.startswith(("javascript:", "mailto:", "tel:", "#")):
            return None
        if url.startswith(("http://", "https://")):
            return url
        try:
            return urljoin(base_url, url)
        except Exception as e:
            logger.warning(f"Failed to make absolute URL from {url} (base: {base_url}): {e}")
            return None

    def _check_resource(self, resource_url: str, resource_type: str) -> Optional[Dict]:
        """Vérifie une ressource unique (avec gestion des erreurs)."""
        try:
            # Utiliser GET au lieu de HEAD pour éviter les 405 (ex: hCaptcha)
            response = self.session.get(
                resource_url,
                timeout=settings.RESOURCE_TIMEOUT,
                allow_redirects=True,
                verify=True,
                stream=True,  # Évite de télécharger le corps pour les images
            )
            if response.status_code >= 400:
                return {
                    "resource_url": resource_url,
                    "resource_type": resource_type,
                    "status_code": response.status_code,
                }
            return None
        except requests.exceptions.RequestException as e:
            return {
                "resource_url": resource_url,
                "resource_type": resource_type,
                "error": str(e),
            }

    def extract_resources(self, page_url: str) -> List[Tuple[str, str]]:
        """Extrait toutes les ressources d'une page et les convertit en URLs absolues."""
        resources = set()
        try:
            self.driver.get(page_url)
            logger.debug(f"Loading page: {page_url}")

            # Scroll pour charger les ressources dynamiques
            self._scroll_to_bottom()

            # === 1. Scripts JS ===
            for script in self.driver.find_elements("tag name", "script"):
                src = script.get_attribute("src")
                if src:
                    absolute_url = self._make_absolute_url(page_url, src)
                    if absolute_url:
                        resources.add((absolute_url, "js"))

            # === 2. Feuilles de style CSS (correction du bug original) ===
            for link in self.driver.find_elements("xpath", "//link[@rel='stylesheet' or contains(@rel, 'style')]"):
                href = link.get_attribute("href")
                if href:
                    absolute_url = self._make_absolute_url(page_url, href)
                    if absolute_url:
                        resources.add((absolute_url, "css"))

            # === 3. Images ===
            for img in self.driver.find_elements("tag name", "img"):
                src = img.get_attribute("src")
                if src:
                    absolute_url = self._make_absolute_url(page_url, src)
                    if absolute_url:
                        resources.add((absolute_url, "image"))

            # === 4. Images de fond (background-image) ===
            import re
            elements_with_bg = self.driver.find_elements(
                "xpath", "//*[contains(@style, 'background-image')]"
            )
            for el in elements_with_bg:
                style = el.get_attribute("style") or ""
                urls = re.findall(r"url\(['\"]?(.*?)['\"]?\)", style)
                for url in urls:
                    absolute_url = self._make_absolute_url(page_url, url)
                    if absolute_url:
                        resources.add((absolute_url, "image"))

            # === 5. Autres ressources (favicons, etc.) ===
            for link in self.driver.find_elements("tag name", "link"):
                href = link.get_attribute("href")
                if href and "icon" in (link.get_attribute("rel") or ""):
                    absolute_url = self._make_absolute_url(page_url, href)
                    if absolute_url:
                        resources.add((absolute_url, "icon"))

            logger.debug(f"Found {len(resources)} resources on {page_url}")
            return list(resources)

        except Exception as e:
            logger.error(f"Error extracting resources from {page_url}: {e}")
            return []

    def _scroll_to_bottom(self):
        """Scroll jusqu'en bas de la page pour charger les ressources dynamiques."""
        import time
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        for _ in range(3):  # Max 3 scrolls
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(settings.SCROLL_DELAY)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def check_page_resources(
        self, page_url: str
    ) -> Tuple[List[Dict], List[Dict]]:
        """Vérifie toutes les ressources d'une page avec parallélisme."""
        resource_errors = []
        console_errors = []

        try:
            # 1. Extraire les ressources
            resources = self.extract_resources(page_url)
            if not resources:
                return resource_errors, console_errors

            # 2. Vérifier les erreurs console
            console_errors = self._get_console_errors(page_url)

            # 3. Vérifier les ressources EN PARALLÈLE
            with ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
                futures = {
                    executor.submit(self._check_resource, url, res_type): (url, res_type)
                    for url, res_type in resources
                }
                for future in as_completed(futures):
                    error = future.result()
                    if error:
                        error["page"] = page_url
                        resource_errors.append(error)

        except Exception as e:
            logger.error(f"Error checking resources for {page_url}: {e}")

        return resource_errors, console_errors

    def _get_console_errors(self, page_url: str) -> List[Dict]:
        """Récupère les erreurs console pour une page."""
        console_errors = []
        try:
            logs = self.driver.get_log("browser")
            for log in logs:
                if log["level"] in ["SEVERE", "ERROR"]:
                    console_errors.append({
                        "page": page_url,
                        "level": log["level"],
                        "message": log["message"],
                    })
        except Exception as e:
            logger.error(f"Error getting console errors for {page_url}: {e}")
        return console_errors