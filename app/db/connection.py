import sqlite3
import os

DB_NAME = "DDA.db"

def get_db_path():
    """Retourne le chemin absolu vers le fichier de la base de données DDA.db."""
    # Le fichier est situé à la racine du projet
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    return os.path.join(project_root, DB_NAME)

def get_connection():
    """Crée et retourne une connexion SQLite ouverte."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    # Activer le support des clés étrangères
    conn.execute("PRAGMA foreign_keys = ON;")
    # Configurer le row_factory pour récupérer les lignes sous forme de dictionnaire/Row
    conn.row_factory = sqlite3.Row
    return conn
