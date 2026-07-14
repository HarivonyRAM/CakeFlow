from app.db.connection import get_connection

class HistoriqueRepository:
    """Gère la persistance de l'historique des statuts des commandes dans la base de données SQLite."""

    def create(self, commande_id, statut_precedent, statut_nouveau, commentaire=None):
        """Crée une nouvelle entrée dans l'historique de la commande."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO historique_commandes (commande_id, statut_precedent, statut_nouveau, commentaire)
                VALUES (?, ?, ?, ?);
            """, (commande_id, statut_precedent, statut_nouveau, commentaire))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_by_commande_id(self, commande_id):
        """Récupère l'historique de modification d'une commande spécifique."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM historique_commandes 
                WHERE commande_id = ? 
                ORDER BY date_modification DESC;
            """, (commande_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def delete_by_commande_id(self, commande_id):
        """Supprime tout l'historique associé à une commande spécifique."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM historique_commandes WHERE commande_id = ?;", (commande_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
