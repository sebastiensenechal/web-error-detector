"""Script d'exécution pour lancer l'application depuis la ligne de commande."""

import argparse

from src.main import main


def parse_args():
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Web Error Detector - Détecte les erreurs sur les sites web"
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="URL de départ pour le crawl (par défaut: START_URL dans .env)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Nombre maximum de pages à crawler",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Nom du fichier de sortie (sans extension)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Active le mode verbose (DEBUG)",
    )
    return parser.parse_args()


def main_cli():
    """Point d'entrée CLI."""
    args = parse_args()

    if args.verbose:
        import logging
        logging.getLogger("web_error_detector").setLevel(logging.DEBUG)

    main(
        start_url=args.url,
        max_pages=args.max_pages,
        filename=args.output,
    )


if __name__ == "__main__":
    main_cli()