from app.repositories.contact_repo import ContactRepository

class ContactService:
    """Service gérant la logique métier pour les contacts des clients."""

    def __init__(self):
        self.contact_repo = ContactRepository()

    def create_contact(self, client_id, objet, num=None, mail=None, autres=None):
        """Crée un nouveau contact pour un client."""
        return self.contact_repo.create(client_id, objet, num, mail, autres)

    def get_contact(self, contact_id):
        """Récupère un contact par son ID."""
        return self.contact_repo.get_by_id(contact_id)

    def get_contacts_by_client(self, client_id):
        """Récupère tous les contacts d'un client."""
        return self.contact_repo.get_by_client_id(client_id)

    def update_contact(self, contact_id, objet, num=None, mail=None, autres=None):
        """Met à jour les informations d'un contact."""
        return self.contact_repo.update(contact_id, objet, num, mail, autres)

    def delete_contact(self, contact_id):
        """Supprime un contact."""
        return self.contact_repo.delete(contact_id)

    def delete_contacts_by_client(self, client_id):
        """Supprime tous les contacts d'un client."""
        return self.contact_repo.delete_by_client_id(client_id)
