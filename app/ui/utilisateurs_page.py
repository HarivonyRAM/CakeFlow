"""
Page de gestion CRUD des utilisateurs.
Accessible uniquement par les utilisateurs avec le rôle 'Admin'.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QComboBox, QMessageBox, QFrame,
    QSizePolicy
)
from PyQt5.QtCore import Qt

from app.repositories.user_repo import UserRepository


# ──────────────────────────────────────────────────────────────
# Dialogue de création / modification d'un utilisateur
# ──────────────────────────────────────────────────────────────

class UserDialog(QDialog):
    """Dialogue modal pour ajouter ou modifier un utilisateur."""

    ROLES = ['Vendeur', 'Admin']

    def __init__(self, parent=None, user_data=None):
        """
        Args:
            parent: widget parent.
            user_data: dict contenant les informations existantes de l'utilisateur
                       (None pour un ajout, dict pour une modification).
        """
        super().__init__(parent)
        self.user_data = user_data
        self.is_edit = user_data is not None
        self._repo = UserRepository()

        self.setWindowTitle("Modifier l'utilisateur" if self.is_edit else "Nouvel utilisateur")
        self.setMinimumWidth(420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._build_ui()

        if self.is_edit:
            self._populate_fields()

    # ── Construction de l'interface ──────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Titre du dialogue
        title = QLabel("Modifier l'utilisateur" if self.is_edit else "Ajouter un utilisateur")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #c2185b;
            }
        """)
        layout.addWidget(title)

        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("QFrame { background-color: #fce4ec; }")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        # Formulaire
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur unique")
        form.addRow("Nom d'utilisateur :", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        placeholder = "Laisser vide pour ne pas changer" if self.is_edit else "Mot de passe"
        self.password_input.setPlaceholderText(placeholder)
        form.addRow("Mot de passe :", self.password_input)

        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Nom de famille")
        form.addRow("Nom :", self.nom_input)

        self.prenom_input = QLineEdit()
        self.prenom_input.setPlaceholderText("Prénom")
        form.addRow("Prénom :", self.prenom_input)

        self.role_combo = QComboBox()
        self.role_combo.addItems(self.ROLES)
        form.addRow("Rôle :", self.role_combo)

        layout.addLayout(form)

        # Boutons d'action
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        btn_cancel = QPushButton("Annuler")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setMinimumWidth(100)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #666666;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #eeeeee;
                border-color: #bdbdbd;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton("Enregistrer")
        btn_save.setFixedHeight(38)
        btn_save.setMinimumWidth(120)
        btn_save.clicked.connect(self._on_save)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

    # ── Pré-remplir les champs en mode édition ───────────────

    def _populate_fields(self):
        self.username_input.setText(self.user_data.get('username', ''))
        self.nom_input.setText(self.user_data.get('nom', '') or '')
        self.prenom_input.setText(self.user_data.get('prenom', '') or '')
        role = self.user_data.get('role', 'Vendeur')
        idx = self.role_combo.findText(role, Qt.MatchFixedString)
        if idx >= 0:
            self.role_combo.setCurrentIndex(idx)

    # ── Validation et sauvegarde ─────────────────────────────

    def _on_save(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        nom = self.nom_input.text().strip()
        prenom = self.prenom_input.text().strip()
        role = self.role_combo.currentText()

        # Validations
        if not username:
            QMessageBox.warning(self, "Champ requis", "Le nom d'utilisateur est obligatoire.")
            return

        if not self.is_edit and not password:
            QMessageBox.warning(self, "Champ requis", "Le mot de passe est obligatoire pour un nouvel utilisateur.")
            return

        # Vérifier l'unicité du username
        existing = self._repo.get_by_username(username)
        if existing:
            # En mode édition, c'est OK si c'est le même utilisateur
            if not self.is_edit or existing['id'] != self.user_data['id']:
                QMessageBox.warning(
                    self, "Nom d'utilisateur existant",
                    f"Le nom d'utilisateur « {username} » est déjà utilisé."
                )
                return

        # Stocker le résultat pour récupération par l'appelant
        self.result_data = {
            'username': username,
            'password': password if password else None,
            'nom': nom or None,
            'prenom': prenom or None,
            'role': role,
        }
        self.accept()


# ──────────────────────────────────────────────────────────────
# Page principale de gestion des utilisateurs
# ──────────────────────────────────────────────────────────────

class UtilisateursPage(QWidget):
    """Widget intégré au QStackedWidget du dashboard pour gérer les utilisateurs."""

    COLUMNS = ['ID', "Nom d'utilisateur", 'Nom', 'Prénom', 'Rôle', 'Actions']

    def __init__(self, parent=None):
        super().__init__(parent)
        self._repo = UserRepository()
        self._build_ui()
        self.refresh_table()

    # ── Construction de l'interface ──────────────────────────

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # ─── En-tête : titre + bouton ajouter ────────────────
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        title = QLabel("Gestion des Utilisateurs")
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #c2185b;
            }
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()

        btn_add = QPushButton("＋  Ajouter un utilisateur")
        btn_add.setFixedHeight(42)
        btn_add.setMinimumWidth(220)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e91e90, stop:1 #c2185b);
                color: #ffffff;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #c2185b, stop:1 #ad1457);
            }
        """)
        btn_add.clicked.connect(self._on_add_user)
        header_layout.addWidget(btn_add)

        main_layout.addLayout(header_layout)

        # ─── Conteneur du tableau ─────────────────────────────
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #f0e0e8;
                border-radius: 16px;
            }
        """)
        table_frame_layout = QVBoxLayout(table_frame)
        table_frame_layout.setContentsMargins(16, 16, 16, 16)
        table_frame_layout.setSpacing(0)

        self._table = QTableWidget()
        self._table.setColumnCount(len(self.COLUMNS))
        self._table.setHorizontalHeaderLabels(self.COLUMNS)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setSelectionMode(QTableWidget.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        self._table.verticalHeader().setVisible(False)
        self._table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: none;
                border-radius: 8px;
                gridline-color: transparent;
            }
            QTableWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #f5e8ee;
            }
            QTableWidget::item:hover {
                background-color: #fff0f3;
            }
            QTableWidget::item:selected {
                background-color: #fce4ec;
                color: #c2185b;
            }
            QTableWidget::item:alternate {
                background-color: #fdf8fa;
            }
        """)

        # Configuration des colonnes
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)   # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)            # Username
        header.setSectionResizeMode(2, QHeaderView.Stretch)            # Nom
        header.setSectionResizeMode(3, QHeaderView.Stretch)            # Prénom
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)   # Rôle
        header.setSectionResizeMode(5, QHeaderView.Fixed)              # Actions
        header.resizeSection(5, 200)

        table_frame_layout.addWidget(self._table)
        main_layout.addWidget(table_frame)

    # ── Rafraîchir le tableau ────────────────────────────────

    def refresh_table(self):
        """Recharge tous les utilisateurs depuis la base de données."""
        users = self._repo.get_all()
        self._table.setRowCount(len(users))

        for row_idx, user in enumerate(users):
            # ID
            id_item = QTableWidgetItem(str(user['id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row_idx, 0, id_item)

            # Nom d'utilisateur
            username_item = QTableWidgetItem(user['username'])
            username_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row_idx, 1, username_item)

            # Nom
            nom_item = QTableWidgetItem(user.get('nom') or '—')
            nom_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row_idx, 2, nom_item)

            # Prénom
            prenom_item = QTableWidgetItem(user.get('prenom') or '—')
            prenom_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row_idx, 3, prenom_item)

            # Rôle (avec badge de couleur)
            role = user.get('role', 'Vendeur')
            role_item = QTableWidgetItem(role)
            role_item.setTextAlignment(Qt.AlignCenter)
            if role == 'Admin':
                role_item.setForeground(Qt.darkMagenta)
            else:
                role_item.setForeground(Qt.darkCyan)
            self._table.setItem(row_idx, 4, role_item)

            # Actions : boutons Modifier / Supprimer
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(6)

            btn_edit = QPushButton("Modifier")
            btn_edit.setFixedHeight(30)
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #fff0f3;
                    color: #c2185b;
                    border: 1px solid #f0c0d0;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0 12px;
                }
                QPushButton:hover {
                    background-color: #fce4ec;
                    border-color: #e91e90;
                }
            """)
            btn_edit.clicked.connect(lambda checked, u=user: self._on_edit_user(u))
            actions_layout.addWidget(btn_edit)

            btn_delete = QPushButton("Supprimer")
            btn_delete.setFixedHeight(30)
            btn_delete.setCursor(Qt.PointingHandCursor)
            btn_delete.setStyleSheet("""
                QPushButton {
                    background-color: #fff5f5;
                    color: #d32f2f;
                    border: 1px solid #ffcdd2;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0 12px;
                }
                QPushButton:hover {
                    background-color: #ffebee;
                    border-color: #ef5350;
                }
            """)
            btn_delete.clicked.connect(lambda checked, u=user: self._on_delete_user(u))
            actions_layout.addWidget(btn_delete)

            self._table.setCellWidget(row_idx, 5, actions_widget)

        # Ajuster la hauteur des lignes
        self._table.resizeRowsToContents()

    # ── Actions CRUD ─────────────────────────────────────────

    def _on_add_user(self):
        """Ouvre le dialogue de création d'un nouvel utilisateur."""
        dialog = UserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.result_data
            try:
                self._repo.create(
                    username=data['username'],
                    password=data['password'],
                    nom=data['nom'],
                    prenom=data['prenom'],
                    role=data['role'],
                )
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de créer l'utilisateur :\n{e}")

    def _on_edit_user(self, user):
        """Ouvre le dialogue de modification d'un utilisateur existant."""
        dialog = UserDialog(self, user_data=user)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.result_data
            try:
                # Mettre à jour les informations de base
                self._repo.update(
                    user_id=user['id'],
                    nom=data['nom'],
                    prenom=data['prenom'],
                    role=data['role'],
                )

                # Mettre à jour le username si modifié
                if data['username'] != user['username']:
                    from app.db.connection import get_connection
                    conn = get_connection()
                    try:
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE users SET username = ? WHERE id = ?;",
                            (data['username'], user['id'])
                        )
                        conn.commit()
                    finally:
                        conn.close()

                # Mettre à jour le mot de passe si fourni
                if data['password']:
                    self._repo.update_password(user['id'], data['password'])

                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de modifier l'utilisateur :\n{e}")

    def _on_delete_user(self, user):
        """Supprime un utilisateur après confirmation."""
        reply = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer l'utilisateur « {user['username']} » ?\n"
            "Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self._repo.delete(user['id'])
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer l'utilisateur :\n{e}")
