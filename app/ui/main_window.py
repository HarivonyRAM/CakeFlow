import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

class DashboardWindow(QMainWindow):
    """Fenêtre principale (Dashboard) de l'application chargée depuis Dashboard.ui"""

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data

        # Chemin du dossier UI et du fichier .ui
        ui_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file = os.path.join(ui_dir, 'Dashboard.ui')

        # Charger le fichier .ui
        uic.loadUi(ui_file, self)

        # Personnaliser le message de bienvenue
        self._setup_welcome_message()

    def _setup_welcome_message(self):
        """Affiche un message de bienvenue personnalisé."""
        if hasattr(self, 'welcomeLabel'):
            nom = self.user_data.get('nom') or ''
            prenom = self.user_data.get('prenom') or ''
            username = self.user_data.get('username') or ''
            
            if prenom or nom:
                nom_complet = f"{prenom} {nom}".strip()
            else:
                nom_complet = username
                
            self.welcomeLabel.setText(f"Bienvenue sur CakeFlow, {nom_complet} !")
            print(f"Dashboard chargé pour l'utilisateur : {nom_complet}")
