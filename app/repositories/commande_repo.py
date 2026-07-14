from app.db.connection import get_connection

class CommandeRepository:
    """Gère la persistance des données commandes dans la base de données SQLite."""

    def create(self, client_id, lieu_type, lieu_adresse=None, prix_total=0.0, accompte=0.0, rap=0.0, date_livraison=None, statut='En attente', details=None):
        """Crée une nouvelle commande."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO commandes (client_id, lieu_type, lieu_adresse, prix_total, accompte, rap, date_livraison, statut, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (client_id, lieu_type, lieu_adresse, prix_total, accompte, rap, date_livraison, statut, details))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_by_id(self, commande_id):
        """Récupère une commande par son identifiant unique."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM commandes WHERE id = ?;", (commande_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_by_id_with_client(self, commande_id):
        """Récupère une commande avec les détails du client associé."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, cl.nom AS client_nom, cl.prenom AS client_prenom, cl.adresse AS client_adresse
                FROM commandes c
                JOIN clients cl ON c.client_id = cl.id
                WHERE c.id = ?;
            """, (commande_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_all(self):
        """Récupère toutes les commandes."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM commandes ORDER BY date_commande DESC;")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_all_with_clients(self):
        """Récupère toutes les commandes avec les informations des clients associés."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, cl.nom AS client_nom, cl.prenom AS client_prenom
                FROM commandes c
                JOIN clients cl ON c.client_id = cl.id
                ORDER BY c.date_commande DESC;
            """)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_by_client_id(self, client_id):
        """Récupère toutes les commandes d'un client."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM commandes WHERE client_id = ? ORDER BY date_commande DESC;", (client_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def update(self, commande_id, lieu_type=None, lieu_adresse=None, prix_total=None, accompte=None, rap=None, date_livraison=None, statut=None, details=None):
        """Met à jour les informations d'une commande."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            fields = []
            params = []
            
            if lieu_type is not None:
                fields.append("lieu_type = ?")
                params.append(lieu_type)
            if lieu_adresse is not None:
                fields.append("lieu_adresse = ?")
                params.append(lieu_adresse)
            if prix_total is not None:
                fields.append("prix_total = ?")
                params.append(prix_total)
            if accompte is not None:
                fields.append("accompte = ?")
                params.append(accompte)
            if rap is not None:
                fields.append("rap = ?")
                params.append(rap)
            if date_livraison is not None:
                fields.append("date_livraison = ?")
                params.append(date_livraison)
            if statut is not None:
                fields.append("statut = ?")
                params.append(statut)
            if details is not None:
                fields.append("details = ?")
                params.append(details)
                
            if not fields:
                return False
                
            params.append(commande_id)
            query = f"UPDATE commandes SET {', '.join(fields)} WHERE id = ?;"
            cursor.execute(query, tuple(params))
            conn.commit()
            
            # Recalculer le reste à payer (RAP) si le prix total ou l'acompte ont changé
            if prix_total is not None or accompte is not None:
                self.recalculate_rap(commande_id)
                
            return cursor.rowcount > 0
        finally:
            conn.close()

    def recalculate_rap(self, commande_id):
        """Calcule et met à jour le RAP (Reste À Payer) d'une commande.
        Formule : RAP = prix_total - accompte - (somme des paiements)
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            # 1. Récupérer prix_total et accompte
            cursor.execute("SELECT prix_total, accompte FROM commandes WHERE id = ?;", (commande_id,))
            row = cursor.fetchone()
            if not row:
                return False
            
            prix_total = row['prix_total']
            accompte = row['accompte']
            
            # 2. Récupérer la somme des paiements
            cursor.execute("SELECT SUM(montant) FROM paiements WHERE commande_id = ?;", (commande_id,))
            pay_sum_row = cursor.fetchone()
            payments_total = pay_sum_row[0] if pay_sum_row[0] is not None else 0.0
            
            # 3. Calculer le nouveau RAP
            new_rap = max(0.0, prix_total - accompte - payments_total)
            
            # 4. Mettre à jour le RAP
            cursor.execute("UPDATE commandes SET rap = ? WHERE id = ?;", (new_rap, commande_id))
            conn.commit()
            return True
        finally:
            conn.close()

    def delete(self, commande_id):
        """Supprime une commande."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM commandes WHERE id = ?;", (commande_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
