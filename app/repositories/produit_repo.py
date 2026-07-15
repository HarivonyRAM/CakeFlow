from app.db.connection import get_connection

class ProduitRepository:
    """Gère la persistance des données produits et leurs relations avec les commandes dans SQLite."""

    def create(self, libelle, prix_min=0.0, description=None):
        """Crée un nouveau produit."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO produits (libelle, prix_min, description)
                VALUES (?, ?, ?);
            """, (libelle, prix_min, description))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_by_id(self, produit_id):
        """Récupère un produit par son identifiant unique."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produits WHERE id = ?;", (produit_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_all(self):
        """Récupère tous les produits de la base de données."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produits ORDER BY libelle ASC;")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def update(self, produit_id, libelle, prix_min=0.0, description=None):
        """Met à jour un produit existant."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE produits
                SET libelle = ?, prix_min = ?, description = ?
                WHERE id = ?;
            """, (libelle, prix_min, description, produit_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete(self, produit_id):
        """Supprime un produit de la base de données."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM produits WHERE id = ?;", (produit_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    # ==================================================================
    # Relations avec les commandes (commande_produits)
    # ==================================================================

    def add_to_commande(self, commande_id, produit_id, quantite, prix_unitaire, notes_personnalisation=None):
        """Associe un produit à une commande avec quantité, prix unitaire et notes de personnalisation."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO commande_produits (commande_id, produit_id, quantite, prix_unitaire, notes_personnalisation)
                VALUES (?, ?, ?, ?, ?);
            """, (commande_id, produit_id, quantite, prix_unitaire, notes_personnalisation))
            conn.commit()
            return True
        finally:
            conn.close()

    def remove_from_commande(self, commande_id, produit_id):
        """Retire un produit d'une commande."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM commande_produits
                WHERE commande_id = ? AND produit_id = ?;
            """, (commande_id, produit_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_by_commande_id(self, commande_id):
        """Récupère tous les produits associés à une commande donnée."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cp.produit_id, p.libelle, cp.quantite, cp.prix_unitaire, cp.notes_personnalisation, p.description
                FROM commande_produits cp
                JOIN produits p ON cp.produit_id = p.id
                WHERE cp.commande_id = ?;
            """, (commande_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def clear_commande_produits(self, commande_id):
        """Supprime tous les produits liés à une commande."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM commande_produits WHERE commande_id = ?;", (commande_id,))
            conn.commit()
            return True
        finally:
            conn.close()
