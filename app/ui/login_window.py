import os
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import uic

from app.services.auth_service import AuthService

class LoginWindow(QWidget):
    """Fenêtre de connexion chargée depuis Login.ui"""
    
    # Signal émis lorsque la connexion est réussie, transmettant les infos de l'utilisateur
    login_successful = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        
        self.auth_service = AuthService()

        # Chemin du dossier UI et du fichier .ui
        ui_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file = os.path.join(ui_dir, 'Login.ui')

        # Charger le fichier .ui
        uic.loadUi(ui_file, self)

        # Supprimer la barre de titre native pour un look custom
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        # Ajouter le bouton de fermeture "X"
        self._add_close_button()

        # Connecter les signaux
        self._setup_connections()

        # État du toggle mot de passe
        self._password_visible = False

    def _add_close_button(self):
        """Crée et positionne le bouton de fermeture '×' en haut à droite."""
        btn_size = 32
        margin = 10

        self._close_btn = QPushButton("×", self)
        self._close_btn.setFixedSize(btn_size, btn_size)
        self._close_btn.setCursor(Qt.PointingHandCursor)
        self._close_btn.setToolTip("Fermer l'application")
        self._close_btn.clicked.connect(self.close)
        self._close_btn.raise_()   # Toujours au-dessus

        self._close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #c2185b;
                font-size: 22px;
                font-weight: bold;
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: #e91e90;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #c2185b;
                color: #ffffff;
            }
        """)

        # Position initiale
        self._close_btn.move(
            self.width() - btn_size - margin,
            margin
        )

    def _setup_connections(self):
        """Connecte les boutons à leurs actions"""
        # Bouton Se connecter
        if hasattr(self, 'loginButton'):
            self.loginButton.clicked.connect(self._on_login)

        # Toggle visibilité mot de passe
        if hasattr(self, 'togglePasswordBtn'):
            self.togglePasswordBtn.clicked.connect(self._toggle_password)

        # Mot de passe oublié
        if hasattr(self, 'forgotPasswordBtn'):
            self.forgotPasswordBtn.clicked.connect(self._on_forgot_password)

        # Permettre la connexion avec Entrée
        if hasattr(self, 'usernameInput'):
            self.usernameInput.returnPressed.connect(self._on_login)
        if hasattr(self, 'passwordInput'):
            self.passwordInput.returnPressed.connect(self._on_login)

    def _toggle_password(self):
        """Bascule la visibilité du mot de passe"""
        self._password_visible = not self._password_visible
        if self._password_visible:
            self.passwordInput.setEchoMode(QLineEdit.Normal)
        else:
            self.passwordInput.setEchoMode(QLineEdit.Password)

    def _on_login(self):
        """Gère la tentative de connexion"""
        username = self.usernameInput.text().strip()
        password = self.passwordInput.text().strip()

        if not username or not password:
            self._show_error("Veuillez remplir tous les champs.")
            return

        # Appeler le service d'authentification pour vérifier en DB
        user = self.auth_service.authenticate(username, password)

        if user:
            self._show_error("")  # Effacer l'erreur
            print("Connexion réussie !")
            # Émettre le signal pour ouvrir le Dashboard
            self.login_successful.emit(user)
        else:
            self._show_error("Nom d'utilisateur ou mot de passe incorrect.")

    def _show_error(self, message):
        """Affiche ou cache le message d'erreur"""
        if hasattr(self, 'errorLabel'):
            if message:
                self.errorLabel.setText(message)
                self.errorLabel.setVisible(True)
            else:
                self.errorLabel.setVisible(False)

    def _on_forgot_password(self):
        """Gère le clic sur 'Mot de passe oublié'"""
        print("Mot de passe oublié cliqué")

    # --- Garder le bouton X ancré en haut à droite lors du redimensionnement ---
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, '_close_btn'):
            btn_size = 32
            margin = 10
            self._close_btn.move(self.width() - btn_size - margin, margin)
            self._close_btn.raise_()

    # --- Permettre de déplacer la fenêtre sans barre de titre ---
    def mousePressEvent(self, event):
        # Ne pas déclencher le drag si on clique sur le bouton de fermeture
        if hasattr(self, '_close_btn') and self._close_btn.underMouse():
            return
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
