from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt5.QtCore import pyqtSignal, Qt

class PaginationWidget(QWidget):
    """Widget de pagination réutilisable pour tous les listings de l'application."""

    page_changed = pyqtSignal(int)  # Émis lors du changement de page (base 1)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.total_items = 0
        self.items_per_page = 20
        self.current_page = 1
        self.item_name_plural = "éléments"
        self._build_ui()

    def _build_ui(self):
        # Layout principal horizontal
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(16, 8, 16, 8)
        self.main_layout.setSpacing(16)

        # Label d'information de pagination à gauche
        self.lbl_info = QLabel("Affichage de 0 à 0 sur 0 éléments")
        self.lbl_info.setStyleSheet("QLabel { font-size: 13px; color: #475569; }")
        self.main_layout.addWidget(self.lbl_info)

        self.main_layout.addStretch()

        # Layout pour les boutons à droite
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(6)
        self.btn_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.btn_layout)

        self._style_sheet = """
            QPushButton {
                background-color: #ffffff;
                color: #475569;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 6px 14px;
                min-width: 32px;
            }
            QPushButton:hover {
                background-color: #f8fafc;
                border-color: #cbd5e1;
            }
            QPushButton:disabled {
                background-color: #ffffff;
                color: #cbd5e1;
                border-color: #f1f5f9;
            }
            QPushButton#activePage {
                background-color: #2563eb;
                color: #ffffff;
                border: none;
            }
            QPushButton#activePage:hover {
                background-color: #1d4ed8;
            }
        """
        self.setStyleSheet(self._style_sheet)

    def setup(self, total_items, items_per_page=20, current_page=1, item_name_plural="éléments"):
        """Configure et met à jour les données de pagination."""
        self.total_items = max(0, total_items)
        self.items_per_page = max(1, items_per_page)
        self.current_page = max(1, current_page)
        self.item_name_plural = item_name_plural

        self.update_ui()

    def update_ui(self):
        """Met à jour l'affichage des informations et des boutons."""
        # Calculer le nombre de pages
        total_pages = max(1, (self.total_items + self.items_per_page - 1) // self.items_per_page)

        # Assurer que la page courante est valide
        if self.current_page > total_pages:
            self.current_page = total_pages

        # Mettre à jour le label de gauche
        if self.total_items == 0:
            self.lbl_info.setText(f"Aucun {self.item_name_plural[:-1]} à afficher")
        else:
            start_idx = (self.current_page - 1) * self.items_per_page + 1
            end_idx = min(self.current_page * self.items_per_page, self.total_items)
            self.lbl_info.setText(
                f"Affichage de {start_idx} à {end_idx} sur {self.total_items} {self.item_name_plural}"
            )

        # Nettoyer l'ancien layout des boutons
        while self.btn_layout.count():
            item = self.btn_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        # Si un seul bouton de page n'est pas nécessaire, on dessine quand même pour uniformiser
        # Bouton Précédent
        btn_prev = QPushButton("Précédent")
        btn_prev.setCursor(Qt.PointingHandCursor)
        btn_prev.setEnabled(self.current_page > 1)
        btn_prev.clicked.connect(lambda: self._go_to_page(self.current_page - 1))
        self.btn_layout.addWidget(btn_prev)

        # Déterminer la plage de pages à afficher
        # Afficher au maximum 5 boutons de pages
        pages_to_show = []
        if total_pages <= 5:
            pages_to_show = list(range(1, total_pages + 1))
        else:
            if self.current_page <= 3:
                pages_to_show = [1, 2, 3, 4, 5]
            elif self.current_page >= total_pages - 2:
                pages_to_show = list(range(total_pages - 4, total_pages + 1))
            else:
                pages_to_show = [
                    self.current_page - 2,
                    self.current_page - 1,
                    self.current_page,
                    self.current_page + 1,
                    self.current_page + 2
                ]

        # Boutons de numéros de pages
        for page in pages_to_show:
            btn_page = QPushButton(str(page))
            btn_page.setCursor(Qt.PointingHandCursor)
            if page == self.current_page:
                btn_page.setObjectName("activePage")
                # Réappliquer la feuille de style locale pour le nom d'objet
                btn_page.setStyleSheet(self._style_sheet)
            btn_page.clicked.connect(lambda checked, p=page: self._go_to_page(p))
            self.btn_layout.addWidget(btn_page)

        # Bouton Suivant
        btn_next = QPushButton("Suivant")
        btn_next.setCursor(Qt.PointingHandCursor)
        btn_next.setEnabled(self.current_page < total_pages)
        btn_next.clicked.connect(lambda: self._go_to_page(self.current_page + 1))
        self.btn_layout.addWidget(btn_next)

    def _go_to_page(self, page):
        """Met à jour la page active et émet le signal."""
        if page != self.current_page:
            self.current_page = page
            self.update_ui()
            self.page_changed.emit(self.current_page)
