from app.db.connection import get_connection

class PaiementRepository:
    """Gère la persistance des paiements pour les commandes dans la base de données SQLite."""

    def _recalculate_commande_rap(self, cursor, commande_id):
        """Met à jour le reste à payer (RAP) de la commande dans la transaction en cours."""
        # 1. Récupérer le total et l'acompte
        cursor.execute("SELECT prix_total, accompte FROM commandes WHERE id = ?;", (commande_id,))
        row = cursor.fetchone()
        if not row:
            return
        
        prix_total = row['prix_total']
        accompte = row['accompte']
        
        # 2. Récupérer la somme des paiements
        cursor.execute("SELECT SUM(montant) FROM paiements WHERE commande_id = ?;", (commande_id,))
        pay_sum_row = cursor.fetchone()
        payments_total = pay_sum_row[0] if pay_sum_row[0] is not None else 0.0
        
        # 3. Calculer le nouveau RAP
        new_rap = max(0.0, prix_total - accompte - payments_total)
        
        # 4. Mettre à jour la commande
        cursor.execute("UPDATE commandes SET rap = ? WHERE id = ?;", (new_rap, commande_id))

    def create(self, commande_id, montant, methode, reference=None):
        """Crée un nouveau paiement et met à jour le RAP de la commande."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO paiements (commande_id, montant, methode, reference)
                VALUES (?, ?, ?, ?);
            """, (commande_id, montant, methode, reference))
            pay_id = cursor.lastrowid
            
            # Recalculer le RAP de la commande
            self._recalculate_commande_rap(cursor, commande_id)
            
            conn.commit()
            return pay_id
        finally:
            conn.close()

    def get_by_id(self, paiement_id):
        """Récupère un paiement par son identifiant unique."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM paiements WHERE id = ?;", (paiement_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_by_commande_id(self, commande_id):
        """Récupère tous les paiements associés à une commande spécifique."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM paiements WHERE commande_id = ? ORDER BY date_paiement DESC;", (commande_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def delete(self, paiement_id):
        """Supprime un paiement et met à jour le RAP de la commande."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            # Récupérer d'abord l'ID de la commande associée
            cursor.execute("SELECT commande_id FROM paiements WHERE id = ?;", (paiement_id,))
            row = cursor.fetchone()
            if not row:
                return False
            
            commande_id = row['commande_id']
            
            # Supprimer le paiement
            cursor.execute("DELETE FROM paiements WHERE id = ?;", (paiement_id,))
            
            # Recalculer le RAP de la commande
            self._recalculate_commande_rap(cursor, commande_id)
            
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
