"""Configuration du MCP server OakLMS."""
import os


def get_base_url() -> str:
    """Retourne l'URL de base OakLMS depuis la variable d'environnement."""
    return os.environ.get("OAKLMS_URL", "http://localhost:8080").rstrip("/")
