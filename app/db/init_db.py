import os
import sys

# Ajouter le dossier racine du projet au sys.path pour permettre les imports absolus
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.connection import get_connection, get_db_path
from app.utils.security import hash_password

def initialize_database():
    db_path = get_db_path()
    print(f"Initialisation de la base de données : {db_path}")
    
    # Créer les dossiers parents s'ils n'existent pas
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Table users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        nom TEXT,
        prenom TEXT,
        role TEXT NOT NULL DEFAULT 'Vendeur'
    );
    """)
    
    # 2. Table clients
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        adresse TEXT
    );
    """)
    
    # 3. Table contacts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        objet TEXT NOT NULL,
        num TEXT,
        mail TEXT,
        autres TEXT,
        FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
    );
    """)
    
    # 4. Table commandes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS commandes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        lieu_type TEXT NOT NULL CHECK(lieu_type IN ('livraison', 'recuperation')),
        lieu_adresse TEXT,
        prix_total REAL NOT NULL DEFAULT 0.0,
        accompte REAL NOT NULL DEFAULT 0.0,
        rap REAL NOT NULL DEFAULT 0.0,
        date_commande TEXT DEFAULT (datetime('now', 'localtime')),
        date_livraison TEXT,
        statut TEXT NOT NULL DEFAULT 'En attente',
        details TEXT,
        FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE RESTRICT
    );
    """)
    
    # 5. Table paiements
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS paiements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        commande_id INTEGER NOT NULL,
        montant REAL NOT NULL,
        date_paiement TEXT DEFAULT (datetime('now', 'localtime')),
        methode TEXT NOT NULL,
        reference TEXT,
        FOREIGN KEY (commande_id) REFERENCES commandes (id) ON DELETE CASCADE
    );
    """)
    
    # 6. Table historique_commandes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historique_commandes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        commande_id INTEGER NOT NULL,
        statut_precedent TEXT,
        statut_nouveau TEXT NOT NULL,
        date_modification TEXT DEFAULT (datetime('now', 'localtime')),
        commentaire TEXT,
        FOREIGN KEY (commande_id) REFERENCES commandes (id) ON DELETE CASCADE
    );
    """)

    # 7. Table produits
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        libelle TEXT NOT NULL,
        prix_min REAL NOT NULL DEFAULT 0.0,
        description TEXT
    );
    """)

    # 8. Table commande_produits (Relation Commande <- Many to Many -> Produit)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS commande_produits (
        commande_id INTEGER NOT NULL,
        produit_id INTEGER NOT NULL,
        quantite INTEGER NOT NULL DEFAULT 1,
        prix_unitaire REAL NOT NULL,
        notes_personnalisation TEXT,
        PRIMARY KEY (commande_id, produit_id),
        FOREIGN KEY (commande_id) REFERENCES commandes (id) ON DELETE CASCADE,
        FOREIGN KEY (produit_id) REFERENCES produits (id) ON DELETE RESTRICT
    );
    """)
    
    # Insérer l'utilisateur SuperAdmin par défaut s'il n'existe pas encore
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?;", ("SuperAdmin",))
    if cursor.fetchone()[0] == 0:
        admin_pass_hash = hash_password("superAdmin")
        cursor.execute("""
        INSERT INTO users (username, password_hash, nom, prenom, role)
        VALUES (?, ?, ?, ?, ?);
        """, ("SuperAdmin", admin_pass_hash, "Super", "Admin", "Admin"))
        print("Utilisateur SuperAdmin créé par défaut : SuperAdmin / superAdmin")
        
    conn.commit()
    conn.close()
    print("Base de données initialisée avec succès.")

if __name__ == "__main__":
    initialize_database()
