import os
from PyQt5.QtGui import QIcon

class NavigationService:
    """Service de routage et de navigation entre les fenêtres de l'application.
    Inspiré du pattern de redirection avec persistance des références.
    """

    @staticmethod
    def addIconToNextWindow(fenetre):
        """Ajoute l'icône de l'application à la nouvelle interface de la fenêtre."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        icon_path = os.path.join(project_root, 'assets', 'images', 'logo.png')
        
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            if hasattr(fenetre, 'interface') and fenetre.interface:
                fenetre.interface.setWindowIcon(icon)
            else:
                fenetre.setWindowIcon(icon)

    @staticmethod
    def toLogin(fenetre):
        """Redirige vers l'écran de connexion."""
        from app.ui.login_window import LoginWindow
        
        fenetre.interface = LoginWindow()
        NavigationService.addIconToNextWindow(fenetre)
        
        # Connecter le signal de succès de connexion
        def handle_success(user_data):
            NavigationService.toDashboard(fenetre.interface, user_data)
            
        fenetre.interface.login_successful.connect(handle_success)
        fenetre.interface.show()
        fenetre.close()

    @staticmethod
    def toDashboard(fenetre, user_data):
        """Redirige vers le tableau de bord principal."""
        from app.ui.main_window import DashboardWindow
        
        fenetre.interface = DashboardWindow(user_data)
        NavigationService.addIconToNextWindow(fenetre)
        fenetre.interface.show()
        fenetre.close()

    @staticmethod
    def toClients(fenetre):
        """Redirige vers la fenêtre de gestion des clients."""
        from app.ui.clients_window import ClientsWindow
        
        # On passe la session de l'utilisateur si nécessaire
        user_data = getattr(fenetre, 'user_data', None)
        fenetre.interface = ClientsWindow(user_data) if user_data else ClientsWindow()
        NavigationService.addIconToNextWindow(fenetre)
        fenetre.interface.show()
        fenetre.close()
