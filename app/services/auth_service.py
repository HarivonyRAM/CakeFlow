from app.repositories.user_repo import UserRepository
from app.utils.security import verify_password

class AuthService:
    """Service gérant l'authentification et les sessions utilisateurs."""

    def __init__(self):
        self.user_repo = UserRepository()

    def authenticate(self, username, password):
        """Vérifie les identifiants de l'utilisateur.
        Retourne les informations de l'utilisateur s'il est authentifié, sinon None.
        """
        user = self.user_repo.get_by_username(username)
        if not user:
            return None
            
        if verify_password(password, user['password_hash']):
            # Retourner l'utilisateur sans le hash du mot de passe pour des raisons de sécurité
            user_data = dict(user)
            user_data.pop('password_hash', None)
            return user_data
            
        return None
