"""
CakeFlow - Délice et Douceur chez A
Application de gestion de pâtisserie

Point d'entrée principal de l'application.
Gère le cycle de vie des fenêtres (Login -> Dashboard) via NavigationService.
"""

import sys
import os

# Ajouter le dossier racine du projet au sys.path pour permettre les imports absolus
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Ajouter le dossier 'ui' au chemin de recherche pour resources_rc
ui_dir = os.path.join(os.path.dirname(__file__), 'ui')
if ui_dir not in sys.path:
    sys.path.append(ui_dir)

# Importer le module de ressources compilées
try:
    # pyrefly: ignore [missing-import]
    import resources_rc
except ImportError:
    from ui import resources_rc

from PyQt5.QtWidgets import QApplication
from app.db.init_db import initialize_database
from app.ui.login_window import LoginWindow
from app.services.navigation_service import NavigationService


def load_stylesheet(app):
    """Charge la feuille de style QSS globale"""
    qss_path = os.path.join(os.path.dirname(__file__), 'ui', 'style.qss')
    if os.path.exists(qss_path):
        with open(qss_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())


def main():
    """Point d'entrée de l'application"""
    # 1. S'assurer que la base de données est initialisée
    initialize_database()

    app = QApplication(sys.argv)

    # 2. Charger le style global
    load_stylesheet(app)

    # 3. Créer la fenêtre de connexion
    login_window = LoginWindow()

    # 4. Connecter le signal de succès au NavigationService
    def on_login_success(user_data):
        NavigationService.toDashboard(login_window, user_data)

    login_window.login_successful.connect(on_login_success)

    # 5. Afficher la fenêtre et démarrer la boucle événements
    login_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
