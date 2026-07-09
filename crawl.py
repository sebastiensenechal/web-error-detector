from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import csv
import re
from datetime import datetime

# Configuration de Selenium
def get_driver():
    # Configuration des options pour Firefox
    options = FirefoxOptions()
    options.add_argument("--headless")  # Mode sans interface
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    # Initialisation du driver Firefox
    driver = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()),
        options=options
    )
    return driver

# Configuration
BASE_URL = "https://insb.cnrs.fr"  # Remplace par l'URL de ton site
START_PATH = "/fr"                # Page de départ
MAX_PAGES = 100                  # Limite pour éviter un crawl infini
DELAY = 1                        # Délai entre les requêtes (en secondes)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Extensions et motifs à exclure
EXCLUDED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.doc', '.docx', '.xls', '.xlsx', '.zip'}
EXCLUDED_PATTERNS = [r'\?', r'\#', r'/admin/', r'/login/', r'/user/']

# Stockage des résultats
visited_urls = set()
error_5xx_urls = []

# Fonction pour vérifier si une URL doit être exclue
def should_exclude(url):
    # Vérifier les motifs (paramètres, ancres, chemins interdits)
    for pattern in EXCLUDED_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return True

    # Vérifier les extensions dans le chemin ou la query
    parsed = urlparse(url)
    path = parsed.path.lower()
    query = parsed.query.lower()

    # Vérifier si le chemin ou la query se termine par une extension exclue
    for ext in EXCLUDED_EXTENSIONS:
        if path.endswith(ext) or query.endswith(ext):
            return True

    return False

# Fonction pour vérifier si une URL est interne au site
def is_internal(url, base_url):
    return urlparse(url).netloc == urlparse(base_url).netloc

# Fonction pour crawler une page
def crawl_page(url):
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        return response.status_code, response.text
    except requests.RequestException as e:
        print(f"Erreur lors de la requête vers {url}: {e}")
        return None, None

# Fonction pour extraire les liens d'une page
def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for link in soup.find_all("a", href=True):
        href = link["href"]
        absolute_url = urljoin(base_url, href)
        if (is_internal(absolute_url, base_url) and
            absolute_url not in visited_urls and
            not should_exclude(absolute_url)):
            links.add(absolute_url)
    return links

# Fonction principale de crawl
def crawl_site(start_url, max_pages):
    queue = [start_url]
    while queue and len(visited_urls) < max_pages:
        current_url = queue.pop(0)
        if current_url in visited_urls:
            continue
        visited_urls.add(current_url)
        print(f"Crawling: {current_url}")

        status_code, html = crawl_page(current_url)
        if status_code is None:
            continue

        if 500 <= status_code <= 599:
            error_5xx_urls.append((current_url, status_code))
            print(f"⚠️ Erreur 5xx trouvée: {current_url} (Code: {status_code})")

        if status_code == 200 and html:
            new_links = extract_links(html, BASE_URL)
            for link in new_links:
                if link not in visited_urls and link not in queue:
                    queue.append(link)

        time.sleep(DELAY)  # Respecter le délai

    return error_5xx_urls

# Lancer le crawl
if __name__ == "__main__":
    start_url = urljoin(BASE_URL, START_PATH)
    print(f"Début du crawl depuis {start_url}...")
    errors = crawl_site(start_url, MAX_PAGES)

    # Afficher les résultats
    print("\n--- Résumé des erreurs 5xx ---")
    for url, code in errors:
        print(f"{url} → {code}")

    print(f"\nTotal des pages visitées: {len(visited_urls)}")
    print(f"Total des erreurs 5xx: {len(errors)}")

# Export to CSV file
def export_to_csv(errors, filename="erreurs_5xx.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["URL", "Code HTTP"])
        for url, code in errors:
            writer.writerow([url, code])
    print(f"Les erreurs ont été exportées vers {filename}")

# Appel à la fin du script
export_to_csv(errors)