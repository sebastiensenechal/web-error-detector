"""Module de crawling du site web."""
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Tuple
from urllib.parse import urljoin

from src.config.settings import settings
from src.utils.logger import logger
from src.utils.url_utils import clean_url, is_same_domain, is_valid_url, normalize_url

class SiteCrawler:
    """Crawler de site web avec détection d'erreurs 5xx."""

    def __init__(self):
        self.visited: set = set()
        self.to_visit: list = []
        self.pages: list = []
        self.page_errors: list = []
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": settings.USER_AGENT})
    
    # ====================================================================
    # Ajout de l'authentification Basic Auth si activée
    # ====================================================================
        if settings.BASIC_AUTH_ENABLED and settings.BASIC_AUTH_USERNAME and settings.BASIC_AUTH_PASSWORD:  # pylint: disable=no-member
            self.session.auth = HTTPBasicAuth(
                settings.BASIC_AUTH_USERNAME,  # pylint: disable=no-member
                settings.BASIC_AUTH_PASSWORD   # pylint: disable=no-member
            )
            logger.info("Basic Auth enabled for crawler")

    def _process_page(self, url: str) -> Tuple[str, Optional[str]]:
        """Traite une page unique et retourne (url, erreur ou None)."""
        try:
            logger.debug(f"Crawling: {url}")
            response = self.session.get(
                url,
                timeout=settings.REQUEST_TIMEOUT,
                allow_redirects=True,
            )
            if response.status_code >= 500:
                error_msg = f"HTTP {response.status_code}"
                logger.error(f"Page error {response.status_code}: {url}")
                return (url, error_msg)
            if response.status_code >= 400:
                logger.warning(f"Page warning {response.status_code}: {url}")
                return (url, f"HTTP {response.status_code}")
            return (url, None)
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(f"Request error for {url}: {e}")
            return (url, error_msg)

    def _extract_links(self, url: str) -> list:
        """Extrait les liens valides d'une page."""
        try:
            response = self.session.get(
                url,
                timeout=settings.REQUEST_TIMEOUT,
                allow_redirects=True,
            )
            soup = BeautifulSoup(response.text, "html.parser")
            links = set()
            for link in soup.find_all("a", href=True):
                next_url = urljoin(url, link["href"])
                next_url = normalize_url(next_url)
                if (
                    is_valid_url(next_url)
                    and is_same_domain(settings.START_URL, next_url)
                    and next_url not in self.visited
                ):
                    links.add(next_url)
            return list(links)
        except Exception as e:
            logger.error(f"Error extracting links from {url}: {e}")
            return []

    def crawl(self, start_url: Optional[str] = None, max_pages: Optional[int] = None) -> Tuple[list, list]:
        """Crawle le site avec parallélisme et découvre les nouvelles pages."""
        start_url = start_url or settings.START_URL
        max_pages = max_pages or settings.MAX_PAGES

        self.to_visit = [start_url]
        self.visited = set()
        self.pages = []
        self.page_errors = []

        logger.info(f"Starting crawl from {start_url}, max pages: {max_pages}")

        with ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
            futures = {}
            while self.to_visit and len(self.pages) < max_pages and len(self.visited) < max_pages:
                # Soumettre de nouvelles tâches tant qu'on a des URLs et de la place
                while self.to_visit and len(futures) < settings.MAX_WORKERS and len(self.visited) < max_pages:
                    current_url = self.to_visit.pop(0)
                    if current_url in self.visited:
                        continue
                    self.visited.add(current_url)
                    future = executor.submit(self._process_page, current_url)
                    futures[future] = current_url

                # Traiter les tâches terminées
                if futures:
                    for future in as_completed(futures):
                        url, error = future.result()
                        futures.pop(future)

                        if error:
                            self.page_errors.append((url, error))
                        else:
                            self.pages.append(url)
                            # Découvrir de nouvelles URLs depuis cette page
                            new_links = self._extract_links(url)
                            self.to_visit.extend(new_links)
                            logger.debug(f"Discovered {len(new_links)} new links from {url}")

        logger.info(f"Crawled {len(self.pages)} pages, found {len(self.page_errors)} errors")
        return self.pages, self.page_errors