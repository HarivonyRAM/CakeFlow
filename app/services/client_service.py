from app.repositories.client_repo import ClientRepository

class ClientService:
    """Service gérant la logique métier pour les clients."""

    def __init__(self):
        self.client_repo = ClientRepository()

    def create_client(self, nom, prenom, adresse=None):
        """Crée un nouveau client."""
        return self.client_repo.create(nom, prenom, adresse)

    def get_client(self, client_id):
        """Récupère un client par son identifiant unique."""
        return self.client_repo.get_by_id(client_id)

    def get_all_clients(self):
        """Récupère la liste de tous les clients."""
        return self.client_repo.get_all()

    def update_client(self, client_id, nom, prenom, adresse=None):
        """Met à jour les informations d'un client."""
        return self.client_repo.update(client_id, nom, prenom, adresse)

    def delete_client(self, client_id):
        """Supprime un client de la base de données."""
        return self.client_repo.delete(client_id)
