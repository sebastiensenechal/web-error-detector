#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour crawler un site, détecter les erreurs 5xx sur les pages,
les erreurs 4xx/5xx sur les ressources (JS, CSS, images) et capturer les erreurs console.
Résultats exportés en JSON.
Nettoyage des URLs : suppression des ancres (#) et paramètres (?).
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# --- Configuration ---
START_URL = "https://www.cnrs.fr/fr/"  # À adapter
MAX_PAGES = 20  # Nombre max de pages à crawler


# --- Fonction pour nettoyer les URLs (supprimer ancres et paramètres) ---
def clean_url(url):
    """Supprime les ancres (#) et paramètres (?) d'une URL."""
    parsed = urlparse(url)
    # On garde seulement le schéma, le domaine et le chemin
    cleaned = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        '',  # params
        '',  # query
        ''   # fragment (ancre)
    ))
    return cleaned


# --- Configuration Selenium ---
def get_selenium_driver():
    """Configure et retourne un driver Selenium avec Chrome."""
    options = Options()
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    options.add_argument("--headless")  # Mode sans interface
    #options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    #options.add_argument("--disable-dev-shm-usage")
    #options.add_argument("--log-level=3")  # Réduit les logs inutiles
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


# --- 1. Crawler le site et détecter les erreurs 5xx sur les pages ---
def crawl_site(start_url, max_pages=MAX_PAGES):
    """Crawle le site et détecte les erreurs 5xx sur les pages."""
    pages = []
    page_errors = []
    visited = set()
    to_visit = [start_url]
    
    while to_visit and len(pages) < max_pages:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue
        
        try:
            response = requests.get(current_url, timeout=10, allow_redirects=True)
            if response.status_code >= 500:
                page_errors.append((current_url, f"HTTP {response.status_code}"))
            else:
                pages.append(current_url)
                visited.add(current_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    next_url = urljoin(current_url, link['href'])
                    next_url = clean_url(next_url)
                    if next_url.startswith(start_url) and next_url not in visited:
                        to_visit.append(next_url)
        except requests.exceptions.RequestException as e:
            page_errors.append((current_url, f"Request failed: {str(e)}"))
    
    return pages, page_errors


# --- 2. Vérifier les ressources et les erreurs console ---
def check_resources_and_console(page_url, driver):
    """Vérifie les erreurs console et les erreurs 4xx/5xx sur les ressources d'une page."""
    resource_errors = []
    console_errors = []

    try:
        driver.get(page_url)
        # Attendre que les ressources soient chargées
        time.sleep(2)  # À ajuster selon la vitesse du site

        # --- NOUVEAU : Scroll jusqu'en bas de la page ---
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll jusqu'en bas
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # Attendre le chargement des nouvelles ressources
            # Calculer la nouvelle hauteur et comparer
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # On a atteint le bas
            last_height = new_height

        # --- 1. Récupérer les erreurs console ---
        logs = driver.get_log("browser")
        for log in logs:
            if log["level"] in ["SEVERE", "ERROR", "WARNING"]:
                console_errors.append({
                    "page": page_url,
                    "level": log["level"],
                    "message": log["message"]
                })

        # --- 2. Récupérer les ressources (JS, CSS, images) ---
        resources = set()
        # Scripts JS
        js_scripts = driver.find_elements("tag name", "script")
        for script in js_scripts:
            src = script.get_attribute("src")
            if src:
                resources.add((src, "js"))

        # Feuille de style CSS
        css_links = driver.find_elements("tag name", "style")
        for link in css_links:
            href = link.get_attribute("href")
            if href and "css" in link.get_attribute("rel"):
                resources.add((href, "css"))

        # Images
        images = driver.find_elements("tag name", "img")
        for img in images:
            src = img.get_attribute("src")
            if src:
                resources.add((src, "image"))

        # --- 3. Vérifier le statut HTTP de chaque ressource ---
        for resource_url, resource_type in resources:
            try:
                response = requests.head(
                    resource_url,
                    timeout=5,
                    allow_redirects=True,
                    verify=True,  # Vérification SSL
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                if response.status_code >= 400:
                    resource_errors.append({
                        "page": page_url,
                        "resource_url": resource_url,
                        "resource_type": resource_type,
                        "status_code": response.status_code
                    })
            except requests.exceptions.RequestException as e:
                resource_errors.append({
                    "page": page_url,
                    "resource_url": resource_url,
                    "resource_type": resource_type,
                    "error": str(e)
                })

    except Exception as e:
        print(f"Erreur lors de la vérification de {page_url}: {e}")

    return resource_errors, console_errors


# --- 3. Enregistrer les résultats en JSON ---
def save_results(page_errors, resource_errors, console_errors, filename="results"):
    """Enregistre les résultats dans un fichier JSON."""
    timestamp = datetime.now().isoformat()
    results = {
        "timestamp": timestamp,
        "page_errors": [{"url": url, "error": error} for url, error in page_errors],
        "resource_errors": resource_errors,
        "console_errors": console_errors
    }
    
    with open(f"{filename}.json", 'w', encoding='utf-8') as file:
        json.dump(results, file, indent=4, ensure_ascii=False)
    
    print(f"Résultats enregistrés dans {filename}.json")


# --- Fonction principale ---
def main(start_url=START_URL, max_pages=MAX_PAGES):
    """Exécute le crawl, la détection des erreurs et l'export des résultats."""
    print(f"Début du crawl pour {start_url}...")
    
    # 1. Crawler le site et détecter les erreurs 5xx sur les pages
    pages, page_errors = crawl_site(start_url, max_pages)
    print(f"Pages crawlées : {len(pages)}")
    print(f"Erreurs 5xx sur les pages : {len(page_errors)}")
    
    # 2. Initialiser Selenium et vérifier les ressources/erreurs console
    driver = get_selenium_driver()
    all_resource_errors = []
    all_console_errors = []
    
    for page in pages:
        print(f"Vérification des ressources et erreurs console pour : {page}")
        resource_errors, console_errors = check_resources_and_console(page, driver)
        all_resource_errors.extend(resource_errors)
        all_console_errors.extend(console_errors)
    
    driver.quit()
    print(f"Erreurs 4xx/5xx sur les ressources : {len(all_resource_errors)}")
    print(f"Erreurs console : {len(all_console_errors)}")
    
    # 3. Enregistrer les résultats
    save_results(page_errors, all_resource_errors, all_console_errors, filename="site_errors")
    print("Traitement terminé.")


# --- Exécution ---
if __name__ == "__main__":
    main(start_url=START_URL, max_pages=MAX_PAGES)