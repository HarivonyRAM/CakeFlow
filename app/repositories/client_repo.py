from app.db.connection import get_connection

class ClientRepository:
    """Gère la persistance des données clients dans la base de données SQLite."""

    def create(self, nom, prenom, adresse=None):
        """Crée un nouveau client."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clients (nom, prenom, adresse)
                VALUES (?, ?, ?);
            """, (nom, prenom, adresse))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_by_id(self, client_id):
        """Récupère un client par son identifiant unique."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients WHERE id = ?;", (client_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_all(self):
        """Récupère la liste de tous les clients."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients ORDER BY nom ASC, prenom ASC;")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def update(self, client_id, nom, prenom, adresse=None):
        """Met à jour les informations d'un client."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE clients
                SET nom = ?, prenom = ?, adresse = ?
                WHERE id = ?;
            """, (nom, prenom, adresse, client_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete(self, client_id):
        """Supprime un client de la base de données."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE id = ?;", (client_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
