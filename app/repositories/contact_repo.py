from app.db.connection import get_connection

class ContactRepository:
    """Gère la persistance des données contacts (liés aux clients) dans la base de données SQLite."""

    def create(self, client_id, objet, num=None, mail=None, autres=None):
        """Crée un nouveau contact pour un client donné."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO contacts (client_id, objet, num, mail, autres)
                VALUES (?, ?, ?, ?, ?);
            """, (client_id, objet, num, mail, autres))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_by_id(self, contact_id):
        """Récupère un contact par son identifiant unique."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = ?;", (contact_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_by_client_id(self, client_id):
        """Récupère tous les contacts associés à un client spécifique."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE client_id = ?;", (client_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def update(self, contact_id, objet, num=None, mail=None, autres=None):
        """Met à jour les informations d'un contact."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE contacts
                SET objet = ?, num = ?, mail = ?, autres = ?
                WHERE id = ?;
            """, (objet, num, mail, autres, contact_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete(self, contact_id):
        """Supprime un contact par son identifiant unique."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE id = ?;", (contact_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete_by_client_id(self, client_id):
        """Supprime tous les contacts associés à un client spécifique."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE client_id = ?;", (client_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
