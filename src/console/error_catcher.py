"""Module dédié à la capture des erreurs console."""

from typing import List, Dict

from selenium.webdriver.remote.webdriver import WebDriver

from src.config.settings import settings
from src.utils.logger import logger


class ConsoleErrorCatcher:
    """Capture les erreurs console du navigateur."""

    def __init__(self, driver: WebDriver):
        self.driver = driver

    def capture_errors(self, page_url: str) -> List[Dict]:
        """
        Capture les erreurs console pour une page.

        Args:
            page_url: URL de la page

        Returns:
            Liste des erreurs console
        """
        errors = []

        try:
            self.driver.get(page_url)
            logger.debug(f"Capturing console errors for: {page_url}")

            # Attendre que la page soit chargée
            import time
            time.sleep(1)

            # Scroll pour déclencher les erreurs potentielles
            self._scroll_page()

            # Récupérer les logs
            logs = self.driver.get_log("browser")

            for log in logs:
                if log["level"] in ["SEVERE", "ERROR"]:
                    errors.append(
                        {
                            "page": page_url,
                            "level": log["level"],
                            "message": log["message"],
                            "timestamp": log.get("timestamp", 0),
                        }
                    )

        except Exception as e:
            logger.error(f"Error capturing console errors for {page_url}: {e}")

        return errors

    def _scroll_page(self):
        """Scroll la page pour déclencher le chargement des ressources."""
        import time

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        for _ in range(3):  # Scroll 3 fois maximum
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(settings.SCROLL_DELAY)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height