from app.db.connection import get_connection
from app.utils.security import hash_password

class UserRepository:
    """Gère la persistance des données utilisateur dans la base de données SQLite."""

    def create(self, username, password, nom=None, prenom=None, role='Vendeur'):
        """Crée un nouvel utilisateur."""
        conn = get_connection()
        try:
            password_hash = hash_password(password)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, password_hash, nom, prenom, role)
                VALUES (?, ?, ?, ?, ?);
            """, (username, password_hash, nom, prenom, role))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_by_id(self, user_id):
        """Récupère un utilisateur par son identifiant unique."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?;", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_by_username(self, username):
        """Récupère un utilisateur par son nom d'utilisateur."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?;", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_all(self):
        """Récupère la liste de tous les utilisateurs."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users;")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def update(self, user_id, nom=None, prenom=None, role=None):
        """Met à jour les informations d'un utilisateur."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            fields = []
            params = []
            
            if nom is not None:
                fields.append("nom = ?")
                params.append(nom)
            if prenom is not None:
                fields.append("prenom = ?")
                params.append(prenom)
            if role is not None:
                fields.append("role = ?")
                params.append(role)
                
            if not fields:
                return False
                
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?;"
            cursor.execute(query, tuple(params))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def update_password(self, user_id, new_password):
        """Met à jour le mot de passe d'un utilisateur en le hachant."""
        conn = get_connection()
        try:
            password_hash = hash_password(new_password)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET password_hash = ? WHERE id = ?;
            """, (password_hash, user_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete(self, user_id):
        """Supprime un utilisateur."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?;", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
