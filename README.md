# Application de Test de Sites Web

Une application Python simple pour crawler des sites web, détecter les erreurs HTTP (4xx/5xx) sur les ressources (JS, CSS, images) et capturer les erreurs de la console navigateur.

---

## 📌 **Fonctionnalités**

- **Crawling** : Exploration des pages d'un site web.
- **Vérification des ressources** : Détection des erreurs HTTP (4xx, 5xx) sur les ressources (JS, CSS, images).
- **Capture des erreurs console** : Récupération des erreurs JavaScript et autres erreurs de la console navigateur.
- **Enregistrement des résultats** : Sauvegarde des erreurs détectées dans un fichier CSV structuré.

---

## 🛠 **Prérequis**

### **Dépendances Python**

Cette application nécessite les bibliothèques suivantes :

- [`selenium`](https://pypi.org/project/selenium/) : Pour simuler un navigateur et capturer les erreurs console.
- [`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/) : Pour parser le HTML et extraire les URLs des ressources.
- [`requests`](https://pypi.org/project/requests/) : Pour faire des requêtes HTTP et vérifier les codes de statut.
- [`webdriver-manager`](https://pypi.org/project/webdriver-manager/) : Pour gérer automatiquement le téléchargement du driver Chrome.

### **Installation des dépendances**

Exécute la commande suivante pour installer toutes les dépendances :

```bash
pip install selenium beautifulsoup4 requests webdriver-manager
```

---

## 🚀 **Utilisation**

### **1. Cloner ou télécharger le projet**

Place-toi dans le répertoire de ton projet et assure-toi que le fichier `crawl.py` (ou le nom que tu as donné à ton script) est présent.

### **2. Exécuter l'application**

Pour lancer l'application, exécute la commande suivante dans ton terminal :

```bash
python crawl.py
```

> **Note** : Par défaut, l'application teste le site `https://insb.cnrs.fr/fr`. Tu peux modifier l'URL de départ directement dans le code (variable `start_url` dans la fonction `main`).

### **3. Personnaliser les paramètres**

Tu peux adapter les paramètres suivants dans le code :

- `start_url` : URL de départ pour le crawl.
- `max_pages` : Nombre maximum de pages à crawler (par défaut : 5).
- `filename` : Nom du fichier CSV de sortie (par défaut : `errors.csv`).

Exemple :

```python
if __name__ == "__main__":
    start_url = "https://mon-site-web.fr"
    main(start_url, max_pages=10)
```

---

## 📂 **Structure du projet**

```
.
├── crawl.py              # Script principal de l'application
├── errors.csv            # Fichier de sortie avec les erreurs détectées (généré automatiquement)
└── README.md             # Documentation du projet
```

---

## 📝 **Fichier de sortie (CSV)**

Les résultats sont enregistrés dans un fichier CSV nommé `errors.csv` (ou un autre nom si tu l'as personnalisé).

### **Format du CSV**


| Type     | Page URL                                   | Resource URL                                                   | Error Details   | Timestamp           |
| -------- | ------------------------------------------ | -------------------------------------------------------------- | --------------- | ------------------- |
| Resource | [https://exemple.com](https://exemple.com) | [https://exemple.com/script.js](https://exemple.com/script.js) | 404             | 2026-07-09T12:00:00 |
| Console  | [https://exemple.com](https://exemple.com) |                                                                | Erreur JS : ... | 2026-07-09T12:00:00 |


- **Type** : `Resource` (erreur HTTP) ou `Console` (erreur navigateur).
- **Page URL** : URL de la page où l'erreur a été détectée.
- **Resource URL** : URL de la ressource en erreur (vide pour les erreurs console).
- **Error Details** : Code d'erreur HTTP (ex: 404) ou message d'erreur console.
- **Timestamp** : Date et heure de détection de l'erreur.

---

## ⚙ **Personnalisation avancée**

### **Modifier le comportement du crawler**

- **Filtrer les URLs** : Ajoute des conditions dans la fonction `crawl_site` pour ignorer certaines URLs (ex: liens externes, PDFs, etc.).
- **Délai entre les requêtes** : Ajoute un `time.sleep()` pour éviter de surcharger le serveur.

### **Améliorer la détection des erreurs**

- **Ignorer les faux positifs** : Filtre les erreurs connues (ex: ressources tierces comme Google Analytics).
- **Ajouter des vérifications** : Détecter les erreurs 4xx/5xx directement dans le HTML (liens brisés).

### **Paralleliser le crawl**

Pour accélérer le processus, tu peux utiliser la bibliothèque `concurrent.futures` pour paralleliser les requêtes. Exemple :

```python
from concurrent.futures import ThreadPoolExecutor

def main(start_url, max_pages=5):
    pages = crawl_site(start_url, max_pages)
    resource_errors = []
    console_errors = []
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        resource_results = list(executor.map(check_resources, pages))
        console_results = list(executor.map(check_console_errors, pages))
    
    for result in resource_results:
        resource_errors.extend(result)
    for result in console_results:
        console_errors.extend(result)
    
    save_results(resource_errors, console_errors)
```

---

## 🐛 **Résolution des problèmes**

### **Problèmes courants**

1. **`webdriver-manager` ne trouve pas Chrome** :
  - Assure-toi que [Google Chrome](https://www.google.com/chrome/) est installé sur ta machine.
  - Si tu utilises un autre navigateur (ex: Firefox), installe le driver correspondant et modifie la configuration dans `get_driver()`.
2. **Erreurs de timeout** :
  - Augmente le délai (`timeout`) dans les requêtes `requests.get()` ou `requests.head()`.
  - Vérifie que le site cible est accessible.
3. **Faux positifs dans les erreurs console** :
  - Certains sites génèrent des erreurs console non critiques (ex: publicités). Filtre-les en adaptant la fonction `check_console_errors`.

---

## 📜 **Licence**

Ce projet est sous licence **MIT**. Tu es libre de l'utiliser, le modifier et le distribuer selon tes besoins.

---

## 🤝 **Contribution**

Si tu souhaites contribuer à ce projet ou signaler un bug, n'hésite pas à ouvrir une issue ou à proposer une pull request.

---

## 📧 **Contact**

Pour toute question ou suggestion, contacte-moi directement.