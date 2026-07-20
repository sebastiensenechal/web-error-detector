# 🔍 Web Error Detector

> **Outil avancé de détection d'erreurs web** – Crawle des sites, vérifie les codes HTTP (4xx/5xx) sur les pages et ressources (JS, CSS, images), et capture les erreurs console du navigateur.
> **Optimisé avec parallélisation** pour des performances accrues.
> **Prend en charge l'authentification Basic Auth** pour les environnements protégés (préproduction, tests).

---

## 🚀 Fonctionnalités
| Fonctionnalité | Description |
|---------------|-------------|
| 🕸️ **Crawling parallèle** | Exploration rapide des pages avec `ThreadPoolExecutor` |
| 🔍 **Vérification des ressources** | Détection des erreurs HTTP (4xx/5xx) sur les ressources JS, CSS, images, polices |
| 💻 **Capture des erreurs console** | Récupération des erreurs JavaScript et warnings du navigateur |
| 📊 **Export structuré** | Résultats au format JSON avec métadonnées et statistiques |
| ⚡ **Performances** | Parallélisation du crawl et des vérifications de ressources |
| 🛡️ **Robuste et sécurisé** | Gestion d'erreurs, timeouts configurables, validation des URLs |
| 🔐 **Authentification Basic Auth** | Prise en charge des sites protégés par authentification HTTP de base |

---

## 📦 Prérequis

- **Python** ≥ 3.10
- **Google Chrome** (recommandé) ou **Firefox**

### Dépendances
```bash
pip install selenium beautifulsoup4 requests webdriver-manager python-dotenv
```

## 🛠 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/tu-org/web-error-detector.git
cd web-error-detector
```

### 2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer l'environnement
```bash
cp .env.example .env
Modifier .env selon tes besoins
```

## ⚙ Configuration
### Fichier .env
```bash
# Crawler
START_URL=https://www.lorem.fr/
MAX_PAGES=20
MAX_DEPTH=3
REQUEST_TIMEOUT=10
SCROLL_DELAY=5
RESOURCE_TIMEOUT=3

# Parallélisation
MAX_WORKERS=4

# Selenium
HEADLESS=true
CHROME_BINARY_PATH=
SCROLL_DELAY=1
RESOURCE_TIMEOUT=3

# Logging
LOG_LEVEL=INFO
LOG_FILE=outputs/crawler.log

# Activer l'authentification Basic Auth pour les requêtes HTTP (crawler et ressources)
BASIC_AUTH_ENABLED=false

# Identifiant pour l'authentification Basic Auth
BASIC_AUTH_USERNAME=

# Mot de passe pour l'authentification Basic Auth
BASIC_AUTH_PASSWORD=
```

## Configuration pour les sites protégés
Pour utiliser l'authentification Basic Auth, appliquez ce qui suit.

⚠️ Important : Les identifiants dans .env sont utilisés par le crawler HTTP (requests), mais Selenium nécessite une configuration séparée.

1. Activez l'authentification dans .env :
```bash
 BASIC_AUTH_ENABLED=true
 BASIC_AUTH_USERNAME=votre_utilisateur
 BASIC_AUTH_PASSWORD=votre_mot_de_passe
 ```
2. Pour Selenium (nécessaire pour le crawling complet) :
- Option 1 : Utilisez une extension navigateur pour Basic Auth
- Option 2 : Intégrez les identifiants dans l'URL de départ : 'https://username:password@lorem.fr'


## 🚀 Utilisation
### Commande de base
```bash
python -m src.main
```
### Avec arguments
```bash
python -m src.scripts.run --url https://example.com --max-pages 10 --output mon_rapport --verbose
```

### Options
| Option | Description | Défaut |
| --- | --- | --- |
| --url | URL de départ | START_URL |
| --max-pages | Nombre max de pages | MAX_PAGES |
| --output | Nom du fichier de sortie | site_errors_{timestamp} |
| --verbose | Mode debug | False |


## 📂 Structure du projet
web_error_detector/
├── src/
│   ├── config/
│   │   └── settings.py          # Configuration (inclut Basic Auth)
│   ├── crawler/
│   │   ├── crawler.py           # Crawler avec Basic Auth
│   │   └── resource_checker.py  # Vérificateur de ressources avec Basic Auth
│   ├── console/
│   │   └── error_catcher.py
│   ├── utils/
│   │   ├── url_utils.py
│   │   ├── logger.py
│   │   └── selenium_utils.py
│   └── main.py
├── scripts/
│   └── run.py
├── outputs/
├── tests/
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md

## 📄 Fichier de sortie (JSON)
### Structure :
```bash
{
  "metadata": {
    "timestamp": "2026-07-20T15:00:00.000000",
    "start_url": "https://www.lorem.fr/",
    "max_pages": 20,
    "basic_auth_enabled": true
  },
  "stats": {
    "pages_crawled": 20,
    "page_errors": 0,
    "resource_errors": 5,
    "console_errors": 2
  },
  "page_errors": [{"url": "url", "error": "HTTP 500"}],
  "resource_errors": [{"page": "url", "resource_url": "url", "resource_type": "js", "status_code": 404}],
  "console_errors": [{"page": "url", "level": "ERROR", "message": "Erreur JS"}]
}
```

## 🔧 Personnalisation
### Ignorer des domaines
```bash
# src/config/settings.py
IGNORED_DOMAINS = {"google-analytics.com", "hcaptcha.com", "facebook.net"}
```

### Ajouter des types de ressources
```bash
# src/config/settings.py
RESOURCE_TYPES = {"js", "css", "image", "font"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"}
```
### Filtrer les codes HTTP
```bash
# src/config/settings.py
IGNORED_STATUS_CODES = {403, 429}
```

## Désactiver Basic Auth pour certains domaines
```bash
# src/config/settings.py
# Ajoutez dans la classe Settings
BASIC_AUTH_EXCLUDED_DOMAINS = {"cdn.public.com", "static.example.com"}
```

## 🔐 Utilisation de l'authentification Basic Auth
### Cas d'usage
- Environnements de préproduction protégés
- Sites de test avec restriction d'accès
- API internes nécessitant une authentification

### Exemple complet
```bash
# Dans .env
START_URL=https://preprod.lorem.fr/
BASIC_AUTH_ENABLED=true
BASIC_AUTH_USERNAME=test_user
BASIC_AUTH_PASSWORD=test_pass123

# Pour Selenium, modifiez START_URL
START_URL=https://test_user:test_pass123@preprod.lorem.fr/
```

## Bonnes pratiques de sécurité
- Ne jamais commiter .env avec des identifiants (il est dans .gitignore)
- Utiliser des variables d'environnement système en production
- Rotater les identifiants régulièrement
- Limiter les permissions de l'utilisateur Basic Auth

## 🐛 Résolution des problèmes
 | Erreur | Cause | Solution |
 | --- | --- | --- |
 | No scheme supplied | URL relative | Vérifier START_URL dans .env (doit commencer par http:// ou https://) |
 | ChromeDriver version mismatch | Version incompatible | Mettre à jour Chrome ou forcer une version de ChromeDriver |
 | 405 Method Not Allowed | CDN bloquant HEAD | Le code utilise GET à la place. Ignorer le domaine dans IGNORED_DOMAINS |
 | Lenteur | Trop de requêtes séquentielles | Augmenter MAX_WORKERS (ex: 8) et réduire RESOURCE_TIMEOUT (ex: 2) |
 | Aucune page crawlée | URL invalide ou site bloquant | Vérifier START_URL et le User-Agent |
 | 401 Unauthorized | Basic Auth manquant | Vérifier BASIC_AUTH_ENABLED, USERNAME et PASSWORD dans .env |
 | 403 Forbidden | Basic Auth incorrect | Vérifier les identifiants et START_URL pour Selenium |

## 📊 Performances
| Workers | Pages/secondes | Temps pour 20 pages |
| --- | --- | --- |
| 1 | ~0.5 | ~40 secondes |
| 4 (défaut) | ~2-3 | ~8-10 secondes |
| 8 | ~4-5 | ~5-6 secondes |

## 🔄 Compatibilité ChromeDriver
| Chrome | ChromeDriver |
| --- | --- |
| 84.x | 84.0.4147.30 |
| 114.x | 114.0.5735.x |
| 120.x | 120.0.6099.x |
| 150.x | 150.0.7830.x |

## 🤝 Contribution
1. Fork le projet
2. git checkout -b feature/ma-fonctionnalité
3. Commit tes changements
4. Push et ouvre une Pull Request

## 📜 Licence
GNU Affero General Public v.3

## 📧 Support
1. Vérifie outputs/crawler.log
2. Consulte ce README
3. Ouvre une issue sur GitHub

© 2026 - Développé avec ❤️ pour la communauté open-source