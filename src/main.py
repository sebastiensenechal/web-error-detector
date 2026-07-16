"""Point d'entrée principal de l'application."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config.settings import settings
from src.crawler.crawler import SiteCrawler
from src.crawler.resource_checker import ResourceChecker
from src.utils.logger import logger
from src.utils.selenium_utils import get_driver


def save_results(
    page_errors: list,
    resource_errors: list,
    console_errors: list,
    filename: Optional[str] = None,
) -> Path:
    """
    Enregistre les résultats dans un fichier JSON.

    Args:
        page_errors: Liste des erreurs de pages
        resource_errors: Liste des erreurs de ressources
        console_errors: Liste des erreurs console
        filename: Nom du fichier de sortie

    Returns:
        Chemin du fichier créé
    """
    filename = filename or f"site_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_path = settings.OUTPUT_DIR / f"{filename}.json"

    results = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "start_url": settings.START_URL,
            "max_pages": settings.MAX_PAGES,
        },
        "stats": {
            "pages_crawled": len(page_errors) + len(resource_errors) + len(console_errors),
            "page_errors": len(page_errors),
            "resource_errors": len(resource_errors),
            "console_errors": len(console_errors),
        },
        "page_errors": [{"url": url, "error": error} for url, error in page_errors],
        "resource_errors": resource_errors,
        "console_errors": console_errors,
    }

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

        logger.info("Results saved to %s", output_path)
        return output_path

    except Exception as e:
        logger.error("Failed to save results: %s", e)
        raise


def main(
    start_url: Optional[str] = None,
    max_pages: Optional[int] = None,
    filename: Optional[str] = None,
):
    """
    Fonction principale de l'application.

    Args:
        start_url: URL de départ
        max_pages: Nombre maximum de pages
        filename: Nom du fichier de sortie
    """
    logger.info("Starting Web Error Detector")

    try:
        # Initialiser le crawler
        crawler = SiteCrawler()

        # Crawler le site
        pages, page_errors = crawler.crawl(start_url, max_pages)
        logger.info("Crawled %d pages", len(pages))

        if not pages:
            logger.warning("No pages crawled. Check your configuration.")
            return

        # Initialiser Selenium
        driver = get_driver()

        try:
            # Initialiser le vérificateur de ressources
            resource_checker = ResourceChecker(driver)

            all_resource_errors = []
            all_console_errors = []

            # Vérifier chaque page
            for page in pages:
                logger.info("Checking resources for: %s", page)
                resource_errors, console_errors = resource_checker.check_page_resources(
                    page
                )
                all_resource_errors.extend(resource_errors)
                all_console_errors.extend(console_errors)

            logger.info(
                "Found %d resource errors and %d console errors", len(all_resource_errors), len(all_console_errors)
                )

        finally:
            driver.quit()
            logger.info("Selenium WebDriver closed")

        # Enregistrer les résultats
        save_results(page_errors, all_resource_errors, all_console_errors, filename)

        logger.info("Processing completed successfully")

    except Exception as e:
        logger.error("Application error: %s", e, exc_info=True)
        raise


if __name__ == "__main__":
    main()
