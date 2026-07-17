"""
Page de gestion CRUD des clients.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt

from app.services.client_service import ClientService
from app.ui.widgets.pagination_widget import PaginationWidget


# ──────────────────────────────────────────────────────────────
# Dialogue de création / modification d'un client
# ──────────────────────────────────────────────────────────────

class ClientDialog(QDialog):
    """Dialogue modal pour ajouter ou modifier un client."""

    def __init__(self, parent=None, client_data=None):
        """
        Args:
            parent: widget parent.
            client_data: dict contenant les informations existantes du client
                         (None pour un ajout, dict pour une modification).
        """
        super().__init__(parent)
        self.client_data = client_data
        self.is_edit = client_data is not None
        self._service = ClientService()

        self.setWindowTitle("Modifier le client" if self.is_edit else "Nouveau client")
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
        title = QLabel("Modifier le client" if self.is_edit else "Ajouter un client")
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

        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Nom de famille (ex: Dupont)")
        form.addRow("Nom :", self.nom_input)

        self.prenom_input = QLineEdit()
        self.prenom_input.setPlaceholderText("Prénom (ex: Jean)")
        form.addRow("Prénom :", self.prenom_input)

        self.adresse_input = QLineEdit()
        self.adresse_input.setPlaceholderText("Adresse postale (optionnelle)")
        form.addRow("Adresse :", self.adresse_input)

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
        self.nom_input.setText(self.client_data.get('nom', ''))
        self.prenom_input.setText(self.client_data.get('prenom', ''))
        self.adresse_input.setText(self.client_data.get('adresse', '') or '')

    # ── Validation et sauvegarde ─────────────────────────────

    def _on_save(self):
        nom = self.nom_input.text().strip()
        prenom = self.prenom_input.text().strip()
        adresse = self.adresse_input.text().strip()

        # Validations
        if not nom:
            QMessageBox.warning(self, "Champ requis", "Le nom du client est obligatoire.")
            return

        if not prenom:
            QMessageBox.warning(self, "Champ requis", "Le prénom du client est obligatoire.")
            return

        self.result_data = {
            'nom': nom,
            'prenom': prenom,
            'adresse': adresse or None,
        }
        self.accept()


# ──────────────────────────────────────────────────────────────
# Page principale de gestion des clients
# ──────────────────────────────────────────────────────────────

class ClientsPage(QWidget):
    """Widget de gestion des clients avec tableau CRUD, tri et pagination."""

    COLUMNS = ['ID', 'Nom', 'Prénom', 'Adresse', 'Actions']

    def __init__(self, parent=None, dashboard=None):
        super().__init__(parent)
        self.dashboard = dashboard
        self._service = ClientService()

        # États pour la pagination et le tri
        self.current_page = 1
        self.items_per_page = 20
        self.sort_column = None
        self.sort_order = Qt.AscendingOrder
        self.all_clients = []
        self.should_reload = True

        self._build_ui()
        self.refresh_table(force_reload=True)

    # ── Construction de l'interface ──────────────────────────

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        # ─── En-tête : titre + bouton ajouter ────────────────
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        title = QLabel("Gestion des Clients")
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #c2185b;
            }
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()

        btn_add = QPushButton("＋  Ajouter un client")
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
        btn_add.clicked.connect(self._on_add_client)
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
        header.setSectionResizeMode(1, QHeaderView.Stretch)            # Nom
        header.setSectionResizeMode(2, QHeaderView.Stretch)            # Prénom
        header.setSectionResizeMode(3, QHeaderView.Stretch)            # Adresse
        header.setSectionResizeMode(4, QHeaderView.Fixed)              # Actions (Contacts, Modifier, Supprimer)
        header.resizeSection(4, 280)

        # Activer l'interaction de tri sur le header
        header.sectionClicked.connect(self._on_header_clicked)

        table_frame_layout.addWidget(self._table)
        main_layout.addWidget(table_frame)

        # Widget de pagination sous le tableau
        self.pagination = PaginationWidget(self)
        self.pagination.page_changed.connect(self._on_page_changed)
        main_layout.addWidget(self.pagination)

        # Initialiser le helper de bulk delete
        from app.ui.widgets.bulk_delete_helper import BulkDeleteHelper
        self.bulk_delete = BulkDeleteHelper(
            table=self._table,
            header_layout=header_layout,
            delete_callback=self._on_bulk_delete_clients,
            refresh_callback=lambda: self.refresh_table(force_reload=True),
            item_name_plural="clients",
            parent=self
        )

    # ── Rafraîchir le tableau ────────────────────────────────

    def refresh_table(self, force_reload=False):
        """Recharge et affiche les clients avec tri et pagination."""
        if force_reload:
            self.should_reload = True

        if self.should_reload:
            try:
                self.all_clients = self._service.get_all_clients()
                self.should_reload = False
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de charger les clients :\n{e}")
                self.all_clients = []

        # Appliquer le tri local complet
        if self.sort_column is not None:
            col_keys = {0: 'id', 1: 'nom', 2: 'prenom', 3: 'adresse'}
            key = col_keys.get(self.sort_column)
            if key:
                reverse = (self.sort_order == Qt.DescendingOrder)
                if key == 'id':
                    self.all_clients.sort(key=lambda x: x.get(key) or 0, reverse=reverse)
                else:
                    self.all_clients.sort(key=lambda x: (x.get(key) or '').lower(), reverse=reverse)

            # Mettre à jour l'indicateur graphique de tri dans l'entête
            self._table.horizontalHeader().setSortIndicator(self.sort_column, self.sort_order)
            self._table.horizontalHeader().setSortIndicatorShown(True)
        else:
            self._table.horizontalHeader().setSortIndicatorShown(False)

        # Calculer le découpage de la pagination
        total_items = len(self.all_clients)
        total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)

        if self.current_page > total_pages:
            self.current_page = total_pages

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_clients = self.all_clients[start_idx:end_idx]

        self._table.setRowCount(len(page_clients))

        for row_idx, client in enumerate(page_clients):
            # Checkbox bulk delete
            self.bulk_delete.add_row_checkbox(row_idx, client['id'])

            # ID
            id_item = QTableWidgetItem(str(client['id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row_idx, 0, id_item)

            # Nom
            nom_item = QTableWidgetItem(client['nom'])
            nom_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row_idx, 1, nom_item)

            # Prénom
            prenom_item = QTableWidgetItem(client['prenom'])
            prenom_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row_idx, 2, prenom_item)

            # Adresse
            adresse_item = QTableWidgetItem(client.get('adresse') or '—')
            adresse_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row_idx, 3, adresse_item)

            # Actions : Contacts / Modifier / Supprimer
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(6)

            # Bouton Contacts
            btn_contacts = QPushButton("Contacts")
            btn_contacts.setFixedHeight(30)
            btn_contacts.setCursor(Qt.PointingHandCursor)
            btn_contacts.setStyleSheet("""
                QPushButton {
                    background-color: #e3f2fd;
                    color: #0d47a1;
                    border: 1px solid #bbdefb;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0 10px;
                }
                QPushButton:hover {
                    background-color: #bbdefb;
                    border-color: #2196f3;
                }
            """)
            btn_contacts.clicked.connect(lambda checked, c=client: self._on_view_contacts(c))
            actions_layout.addWidget(btn_contacts)

            # Bouton Modifier
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
                    padding: 0 10px;
                }
                QPushButton:hover {
                    background-color: #fce4ec;
                    border-color: #e91e90;
                }
            """)
            btn_edit.clicked.connect(lambda checked, c=client: self._on_edit_client(c))
            actions_layout.addWidget(btn_edit)

            # Bouton Supprimer
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
                    padding: 0 10px;
                }
                QPushButton:hover {
                    background-color: #ffebee;
                    border-color: #ef5350;
                }
            """)
            btn_delete.clicked.connect(lambda checked, c=client: self._on_delete_client(c))
            actions_layout.addWidget(btn_delete)

            self._table.setCellWidget(row_idx, 4, actions_widget)

        # Ajuster la hauteur des lignes
        self._table.resizeRowsToContents()

        # Configurer le widget de pagination avec les données fraîches
        self.pagination.setup(
            total_items=total_items,
            items_per_page=self.items_per_page,
            current_page=self.current_page,
            item_name_plural="clients"
        )

    # ── Événements de Tri et de Pagination ───────────────────

    def _on_header_clicked(self, column_idx):
        """Gère le clic sur les entêtes de colonne pour trier les données."""
        if column_idx == 4:  # La colonne Actions n'est pas triable
            return

        if self.sort_column == column_idx:
            # Inverser l'ordre
            self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            self.sort_column = column_idx
            self.sort_order = Qt.AscendingOrder

        self.current_page = 1
        self.refresh_table(force_reload=False)

    def _on_page_changed(self, page_number):
        """Gère le changement de page active."""
        self.current_page = page_number
        self.refresh_table(force_reload=False)

    # ── Actions CRUD ─────────────────────────────────────────

    def _on_add_client(self):
        """Ouvre le dialogue de création d'un client."""
        dialog = ClientDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.result_data
            try:
                self._service.create_client(
                    nom=data['nom'],
                    prenom=data['prenom'],
                    adresse=data['adresse']
                )
                self.refresh_table(force_reload=True)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de créer le client :\n{e}")

    def _on_edit_client(self, client):
        """Ouvre le dialogue de modification d'un client."""
        dialog = ClientDialog(self, client_data=client)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.result_data
            try:
                self._service.update_client(
                    client_id=client['id'],
                    nom=data['nom'],
                    prenom=data['prenom'],
                    adresse=data['adresse']
                )
                self.refresh_table(force_reload=True)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de modifier le client :\n{e}")

    def _on_delete_client(self, client):
        """Supprime un client après confirmation."""
        reply = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer le client « {client['prenom']} {client['nom']} » ainsi que tous ses contacts associés ?\n"
            "Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                # Supprimer d'abord les contacts liés au client (nettoyage explicite)
                from app.services.contact_service import ContactService
                contact_service = ContactService()
                contact_service.delete_contacts_by_client(client['id'])

                # Puis supprimer le client
                self._service.delete_client(client['id'])
                self.refresh_table(force_reload=True)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer le client :\n{e}")

    def _on_bulk_delete_clients(self, client_ids):
        """Supprime plusieurs clients."""
        from app.services.contact_service import ContactService
        contact_service = ContactService()
        for client_id in client_ids:
            # Supprimer d'abord les contacts liés au client
            contact_service.delete_contacts_by_client(client_id)
            # Puis supprimer le client
            self._service.delete_client(client_id)

    def _on_view_contacts(self, client):
        """Navigue vers la page des contacts du client."""
        if self.dashboard:
            client_name = f"{client['prenom']} {client['nom']}"
            self.dashboard.navigate_to_contacts(client['id'], client_name)
