import os
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidgetItem, QHeaderView, QButtonGroup
)
from PyQt5.QtCore import Qt
from PyQt5 import uic

from app.db.connection import get_connection


class DashboardWindow(QMainWindow):
    """Fenêtre principale (Dashboard) de l'application chargée depuis Dashboard.ui"""

    # Mapping : nom du bouton sidebar → (index page, titre header)
    PAGE_MAP = {
        'btnDashboard':    (0, 'Tableau de bord'),
        'btnCommandes':    (1, 'Commandes'),
        'btnClients':      (2, 'Clients'),
        'btnProduits':     (3, 'Produits'),
        'btnPaiements':    (4, 'Paiements'),
        'btnContacts':     (5, 'Contacts'),
    }

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data

        # Chemin du dossier UI et du fichier .ui
        ui_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file = os.path.join(ui_dir, 'Dashboard.ui')

        # Charger le fichier .ui
        uic.loadUi(ui_file, self)

        # 1. Charger les widgets enfants (Sidebar + Header) dans les containers
        self._load_sidebar()
        self._load_header()

        # 2. Connecter les boutons de navigation
        self._setup_navigation()

        # 3. Personnaliser le message de bienvenue
        self._setup_welcome_message()

        # 4. Configurer le tableau des dernières commandes
        self._setup_recent_orders_table()

        # 5. Peupler les statistiques depuis la DB
        self._refresh_stats()

        # 6. Peupler les dernières commandes
        self._refresh_recent_orders()

        # 7. Connecter les boutons d'actions rapides
        self._setup_quick_actions()

    # ==================================================================
    # Chargement des sous-widgets
    # ==================================================================

    def _load_sidebar(self):
        """Charge Sidebar.ui dans le container sidebarContainer."""
        ui_dir = os.path.dirname(os.path.abspath(__file__))
        sidebar_ui = os.path.join(ui_dir, 'widgets', 'Sidebar.ui')

        if hasattr(self, 'sidebarContainer'):
            layout = QVBoxLayout(self.sidebarContainer)
            layout.setContentsMargins(0, 0, 0, 0)

            # Créer un QFrame temporaire pour charger le .ui
            from PyQt5.QtWidgets import QFrame
            self._sidebar = QFrame()
            uic.loadUi(sidebar_ui, self._sidebar)
            layout.addWidget(self._sidebar)

    def _load_header(self):
        """Charge Header.ui dans le container headerContainer."""
        ui_dir = os.path.dirname(os.path.abspath(__file__))
        header_ui = os.path.join(ui_dir, 'widgets', 'Header.ui')

        if hasattr(self, 'headerContainer'):
            layout = QHBoxLayout(self.headerContainer)
            layout.setContentsMargins(0, 0, 0, 0)

            from PyQt5.QtWidgets import QFrame
            self._header = QFrame()
            uic.loadUi(header_ui, self._header)
            layout.addWidget(self._header)

            # Mettre à jour le nom d'utilisateur dans le header
            if hasattr(self._header, 'userName'):
                nom = self.user_data.get('nom') or ''
                prenom = self.user_data.get('prenom') or ''
                username = self.user_data.get('username') or ''
                display_name = f"{prenom} {nom}".strip() or username
                self._header.userName.setText(display_name)

    # ==================================================================
    # Navigation Sidebar ↔ QStackedWidget
    # ==================================================================

    def _setup_navigation(self):
        """Connecte chaque bouton de la sidebar au QStackedWidget."""
        # Créer un QButtonGroup pour gérer l'exclusion mutuelle
        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)

        for btn_name, (page_index, page_title) in self.PAGE_MAP.items():
            btn = self._sidebar.findChild(QPushButton, btn_name)
            if btn:
                self._nav_group.addButton(btn, page_index)
                btn.clicked.connect(
                    lambda checked, idx=page_index, title=page_title: self._navigate_to(idx, title)
                )

        # Connecter le bouton de déconnexion
        btn_logout = self._sidebar.findChild(QPushButton, 'btnLogout')
        if btn_logout:
            btn_logout.clicked.connect(self._on_logout)

    def _navigate_to(self, page_index, page_title):
        """Navigue vers la page demandée et met à jour le header."""
        if hasattr(self, 'pagesStack'):
            self.pagesStack.setCurrentIndex(page_index)

        if hasattr(self, '_header') and hasattr(self._header, 'pageTitle'):
            self._header.pageTitle.setText(page_title)

        # Rafraîchir les stats quand on revient au dashboard
        if page_index == 0:
            self._refresh_stats()
            self._refresh_recent_orders()

    def _on_logout(self):
        """Gère la déconnexion."""
        from app.services.navigation_service import NavigationService
        NavigationService.toLogin(self)

    # ==================================================================
    # Message de bienvenue
    # ==================================================================

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

    # ==================================================================
    # Statistiques
    # ==================================================================

    def _refresh_stats(self):
        """Récupère et affiche les statistiques depuis la base de données."""
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Ventes du jour (somme des prix_total des commandes payées aujourd'hui)
            cursor.execute("""
                SELECT COALESCE(SUM(prix_total), 0)
                FROM commandes
                WHERE date(date_commande) = date('now', 'localtime')
            """)
            ventes_jour = cursor.fetchone()[0]

            # Ventes de la semaine
            cursor.execute("""
                SELECT COALESCE(SUM(prix_total), 0)
                FROM commandes
                WHERE date(date_commande) >= date('now', 'localtime', '-7 days')
            """)
            ventes_semaine = cursor.fetchone()[0]

            # Commandes en cours (statut != 'Livrée' et != 'Annulée')
            cursor.execute("""
                SELECT COUNT(*)
                FROM commandes
                WHERE statut NOT IN ('Livrée', 'Annulée')
            """)
            commandes_en_cours = cursor.fetchone()[0]

            # Clients actifs (clients ayant au moins une commande en cours)
            cursor.execute("""
                SELECT COUNT(DISTINCT client_id)
                FROM commandes
                WHERE statut NOT IN ('Livrée', 'Annulée')
            """)
            clients_actifs = cursor.fetchone()[0]

            conn.close()

            # Mettre à jour les labels
            if hasattr(self, 'cardVentesJourValue'):
                self.cardVentesJourValue.setText(f"{ventes_jour:,.0f} Ar")
            if hasattr(self, 'cardVentesSemaineValue'):
                self.cardVentesSemaineValue.setText(f"{ventes_semaine:,.0f} Ar")
            if hasattr(self, 'cardCommandesValue'):
                self.cardCommandesValue.setText(str(commandes_en_cours))
            if hasattr(self, 'cardClientsValue'):
                self.cardClientsValue.setText(str(clients_actifs))

        except Exception as e:
            print(f"Erreur lors du chargement des statistiques : {e}")

    # ==================================================================
    # Tableau des dernières commandes
    # ==================================================================

    def _setup_recent_orders_table(self):
        """Configure le tableau des dernières commandes."""
        if hasattr(self, 'recentOrdersTable'):
            table = self.recentOrdersTable
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

            table.verticalHeader().setVisible(False)
            table.setSelectionMode(table.SingleSelection)

    def _refresh_recent_orders(self):
        """Charge les 10 dernières commandes dans le tableau."""
        if not hasattr(self, 'recentOrdersTable'):
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT c.id, cl.nom || ' ' || cl.prenom AS client,
                       c.prix_total, c.date_livraison, c.statut
                FROM commandes c
                LEFT JOIN clients cl ON c.client_id = cl.id
                ORDER BY c.date_commande DESC
                LIMIT 10
            """)
            rows = cursor.fetchall()
            conn.close()

            table = self.recentOrdersTable
            table.setRowCount(len(rows))

            for row_idx, row_data in enumerate(rows):
                for col_idx, value in enumerate(row_data):
                    display_value = str(value) if value is not None else '—'
                    if col_idx == 2:  # Montant
                        display_value = f"{value:,.0f} Ar" if value else '0 Ar'
                    item = QTableWidgetItem(display_value)
                    item.setTextAlignment(Qt.AlignCenter)

                    # Colorer le statut
                    if col_idx == 4:
                        if value == 'En attente':
                            item.setForeground(Qt.darkYellow)
                        elif value == 'Livrée':
                            item.setForeground(Qt.darkGreen)
                        elif value == 'Annulée':
                            item.setForeground(Qt.red)

                    table.setItem(row_idx, col_idx, item)

        except Exception as e:
            print(f"Erreur lors du chargement des commandes récentes : {e}")

    # ==================================================================
    # Actions rapides
    # ==================================================================

    def _setup_quick_actions(self):
        """Connecte les boutons d'actions rapides."""
        if hasattr(self, 'btnNouvelleCommande'):
            self.btnNouvelleCommande.clicked.connect(
                lambda: self._navigate_to(1, 'Commandes')
            )

        if hasattr(self, 'btnAjouterClient'):
            self.btnAjouterClient.clicked.connect(
                lambda: self._navigate_to(2, 'Clients')
            )
