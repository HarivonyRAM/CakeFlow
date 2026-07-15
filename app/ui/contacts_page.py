"""
Page de gestion des contacts d'un client.
Affiche les contacts sous forme de cartes fluides et responsives.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QFrame, QDialog, QFormLayout, QLineEdit,
    QTextEdit, QMessageBox, QSizePolicy, QLayout
)
from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PyQt5.QtGui import QIcon, QFont

from app.services.contact_service import ContactService


# ──────────────────────────────────────────────────────────────
# Layout Fluide (FlowLayout) pour positionner les cartes
# ──────────────────────────────────────────────────────────────

class FlowLayout(QLayout):
    """Layout personnalisé qui positionne ses éléments de gauche à droite
    et passe à la ligne suivante si l'espace horizontal est insuffisant.
    """
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margin, _, _, _ = self.getContentsMargins()
        size += QSize(2 * margin, 2 * margin)
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self.itemList:
            wid = item.widget()
            space_x = spacing
            if space_x == -1:
                space_x = wid.style().layoutSpacing(
                    QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal
                )
            space_y = spacing
            if space_y == -1:
                space_y = wid.style().layoutSpacing(
                    QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical
                )

            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()


# ──────────────────────────────────────────────────────────────
# Carte de contact (ContactCard)
# ──────────────────────────────────────────────────────────────

class ContactCard(QFrame):
    """Carte de contact avec design soigné et ombré."""

    def __init__(self, contact, parent_page):
        super().__init__()
        self.contact = contact
        self.parent_page = parent_page
        self._build_ui()

    def _build_ui(self):
        self.setMinimumSize(320, 180)
        self.setMaximumSize(360, 240)
        self.setObjectName("ContactCard")
        self.setStyleSheet("""
            QFrame#ContactCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
            QFrame#ContactCard:hover {
                border-color: #c2185b;
                background-color: #fffbfd;
            }
        """)

        card_layout = QVBoxLayout(self)
        card_layout.setContentsMargins(16, 16, 16, 12)
        card_layout.setSpacing(12)

        # ─── En-tête de la carte : Icône + Objet ───
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # Icône Avatar
        avatar = QLabel("👤")
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                color: #1e88e5;
                font-size: 18px;
                border-radius: 18px;
            }
        """)
        header_layout.addWidget(avatar)

        # Objet empilé
        obj_text_layout = QVBoxLayout()
        obj_text_layout.setSpacing(2)
        
        lbl_obj_title = QLabel("OBJET")
        lbl_obj_title.setStyleSheet("QLabel { font-size: 10px; font-weight: bold; color: #94a3b8; }")
        obj_text_layout.addWidget(lbl_obj_title)

        lbl_obj_value = QLabel(self.contact['objet'])
        lbl_obj_value.setWordWrap(True)
        lbl_obj_value.setStyleSheet("QLabel { font-size: 13px; font-weight: bold; color: #1e293b; }")
        obj_text_layout.addWidget(lbl_obj_value)
        
        header_layout.addLayout(obj_text_layout)
        card_layout.addLayout(header_layout)

        # ─── Infos de contact : E-mail & Téléphone & Autres ───
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)

        # E-mail
        email = self.contact.get('mail') or '—'
        email_layout = QHBoxLayout()
        email_layout.setSpacing(8)
        lbl_mail_icon = QLabel("✉")
        lbl_mail_icon.setStyleSheet("QLabel { color: #94a3b8; font-size: 14px; }")
        lbl_mail_value = QLabel(email)
        lbl_mail_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lbl_mail_value.setStyleSheet("QLabel { color: #475569; font-size: 12px; }")
        email_layout.addWidget(lbl_mail_icon)
        email_layout.addWidget(lbl_mail_value)
        email_layout.addStretch()
        info_layout.addLayout(email_layout)

        # Téléphone
        phone = self.contact.get('num') or '—'
        phone_layout = QHBoxLayout()
        phone_layout.setSpacing(8)
        lbl_phone_icon = QLabel("📞")
        lbl_phone_icon.setStyleSheet("QLabel { color: #94a3b8; font-size: 14px; }")
        lbl_phone_value = QLabel(phone)
        lbl_phone_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lbl_phone_value.setStyleSheet("QLabel { color: #475569; font-size: 12px; }")
        phone_layout.addWidget(lbl_phone_icon)
        phone_layout.addWidget(lbl_phone_value)
        phone_layout.addStretch()
        info_layout.addLayout(phone_layout)

        # Autres informations (optionnel)
        autres = self.contact.get('autres')
        if autres:
            autres_layout = QHBoxLayout()
            autres_layout.setSpacing(8)
            lbl_autres_icon = QLabel("📝")
            lbl_autres_icon.setStyleSheet("QLabel { color: #94a3b8; font-size: 14px; }")
            lbl_autres_value = QLabel(autres)
            lbl_autres_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            lbl_autres_value.setStyleSheet("QLabel { color: #475569; font-size: 12px; }")
            lbl_autres_value.setWordWrap(True)
            autres_layout.addWidget(lbl_autres_icon)
            autres_layout.addWidget(lbl_autres_value)
            autres_layout.addStretch()
            info_layout.addLayout(autres_layout)

        card_layout.addLayout(info_layout)

        # Séparateur
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("QFrame { background-color: #f1f5f9; }")
        line.setFixedHeight(1)
        card_layout.addWidget(line)

        # ─── Pied de carte : Actions de modification / suppression ───
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.addStretch()

        # Modifier
        btn_edit = QPushButton("Modifier")
        btn_edit.setFixedHeight(30)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setStyleSheet("""
            QPushButton {
                background-color: #fff0f3;
                color: #c2185b;
                border: 1px solid #f0c0d0;
                border-radius: 8px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 12px;
            }
            QPushButton:hover {
                background-color: #fce4ec;
                border-color: #e91e90;
            }
        """)
        btn_edit.clicked.connect(self._on_edit)
        footer_layout.addWidget(btn_edit)

        # Supprimer
        btn_delete = QPushButton("Supprimer")
        btn_delete.setFixedHeight(30)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #fff5f5;
                color: #d32f2f;
                border: 1px solid #ffcdd2;
                border-radius: 8px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 12px;
            }
            QPushButton:hover {
                background-color: #ffebee;
                border-color: #ef5350;
            }
        """)
        btn_delete.clicked.connect(self._on_delete)
        footer_layout.addWidget(btn_delete)

        card_layout.addLayout(footer_layout)

    def _on_edit(self):
        self.parent_page.edit_contact(self.contact)

    def _on_delete(self):
        self.parent_page.delete_contact(self.contact)


# ──────────────────────────────────────────────────────────────
# Dialogue modal ContactDialog
# ──────────────────────────────────────────────────────────────

class ContactDialog(QDialog):
    """Dialogue pour ajouter ou modifier un contact."""

    def __init__(self, parent=None, contact_data=None):
        super().__init__(parent)
        self.contact_data = contact_data
        self.is_edit = contact_data is not None
        self._service = ContactService()

        self.setWindowTitle("Modifier le contact" if self.is_edit else "Nouveau contact")
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._build_ui()

        if self.is_edit:
            self._populate_fields()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Titre
        title = QLabel("Modifier le contact" if self.is_edit else "Ajouter un contact")
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

        self.objet_input = QLineEdit()
        self.objet_input.setPlaceholderText("Objet (ex: Inspecteur : Philippe Courtois)")
        form.addRow("Objet :", self.objet_input)

        self.mail_input = QLineEdit()
        self.mail_input.setPlaceholderText("Adresse e-mail (optionnelle)")
        form.addRow("E-mail :", self.mail_input)

        self.num_input = QLineEdit()
        self.num_input.setPlaceholderText("Téléphone (ex: 0663048646)")
        form.addRow("Téléphone :", self.num_input)

        self.autres_input = QTextEdit()
        self.autres_input.setPlaceholderText("Autres détails (notes, horaires, etc.)")
        self.autres_input.setMaximumHeight(80)
        form.addRow("Autres :", self.autres_input)

        layout.addLayout(form)

        # Actions
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

    def _populate_fields(self):
        self.objet_input.setText(self.contact_data.get('objet', ''))
        self.mail_input.setText(self.contact_data.get('mail', '') or '')
        self.num_input.setText(self.contact_data.get('num', '') or '')
        self.autres_input.setText(self.contact_data.get('autres', '') or '')

    def _on_save(self):
        objet = self.objet_input.text().strip()
        mail = self.mail_input.text().strip()
        num = self.num_input.text().strip()
        autres = self.autres_input.toPlainText().strip()

        if not objet:
            QMessageBox.warning(self, "Champ requis", "Le champ Objet est obligatoire.")
            return

        self.result_data = {
            'objet': objet,
            'mail': mail or None,
            'num': num or None,
            'autres': autres or None
        }
        self.accept()


# ──────────────────────────────────────────────────────────────
# Page principale des Contacts (ContactsPage)
# ──────────────────────────────────────────────────────────────

class ContactsPage(QWidget):
    """Widget affichant les contacts d'un client spécifique."""

    def __init__(self, parent=None, dashboard=None):
        super().__init__(parent)
        self.dashboard = dashboard
        self.client_id = None
        self.client_name = ""
        self.sort_asc = True  # Tri par défaut ascendant

        self._service = ContactService()
        self._build_ui()

    def _build_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(20)

        # ─── En-tête de la page ───
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # Bouton retour ←
        btn_back = QPushButton("← Retour")
        btn_back.setFixedHeight(36)
        btn_back.setMinimumWidth(100)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.setToolTip("Retour à la liste des clients")
        btn_back.setStyleSheet("""
            QPushButton {
                background-color: #fff0f3;
                color: #c2185b;
                border: 1px solid #f0c0d0;
                border-radius: 10px;
                font-size: 13px;
                font-weight: bold;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #fce4ec;
                border-color: #e91e90;
            }
        """)
        btn_back.clicked.connect(self._on_back_clicked)
        header_layout.addWidget(btn_back)

        # Titre de la page
        self.title_label = QLabel("Liste des contacts")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #1e293b;
            }
        """)
        header_layout.addWidget(self.title_label)

        # Badge de décompte des contacts
        self.count_badge = QLabel("0")
        self.count_badge.setAlignment(Qt.AlignCenter)
        self.count_badge.setStyleSheet("""
            QLabel {
                background-color: #e0f2fe;
                color: #0369a1;
                font-size: 12px;
                font-weight: bold;
                border-radius: 10px;
                padding: 2px 8px;
                min-width: 16px;
            }
        """)
        header_layout.addWidget(self.count_badge)

        header_layout.addStretch()

        # Bouton Trier par objet
        self.btn_sort = QPushButton("⇅ Trier par objet")
        self.btn_sort.setFixedHeight(36)
        self.btn_sort.setCursor(Qt.PointingHandCursor)
        self.btn_sort.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #475569;
                border: 1px solid #cbd5e1;
                border-radius: 10px;
                font-size: 13px;
                font-weight: normal;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #f8fafc;
                border-color: #94a3b8;
            }
        """)
        self.btn_sort.clicked.connect(self._on_toggle_sort)
        header_layout.addWidget(self.btn_sort)

        # Bouton ajouter contact (couleur primary)
        btn_add = QPushButton("＋ Ajouter un contact")
        btn_add.setFixedHeight(40)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e91e90, stop:1 #c2185b);
                color: #ffffff;
                border: none;
                border-radius: 20px;
                font-size: 13px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #c2185b, stop:1 #ad1457);
            }
        """)
        btn_add.clicked.connect(self._on_add_contact)
        header_layout.addWidget(btn_add)

        self.main_layout.addLayout(header_layout)

        # ─── Zone défilante des cartes (ScrollArea) ───
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background-color: transparent;")
        self.cards_layout = FlowLayout(margin=4, spacing=16)
        self.scroll_widget.setLayout(self.cards_layout)
        self.scroll_area.setWidget(self.scroll_widget)

        self.main_layout.addWidget(self.scroll_area)

    def set_client(self, client_id, client_name):
        """Met à jour le client courant et charge ses contacts."""
        self.client_id = client_id
        self.client_name = client_name
        self.load_contacts()

    def load_contacts(self):
        """Charge les contacts du client courant dans le layout."""
        # Supprimer les anciens widgets du layout
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        if self.client_id is None:
            self.count_badge.setText("0")
            return

        # Récupérer les contacts
        contacts = self._service.get_contacts_by_client(self.client_id)

        # Appliquer le tri
        contacts.sort(
            key=lambda x: (x.get('objet') or '').lower(),
            reverse=not self.sort_asc
        )

        # Mettre à jour le badge de décompte
        self.count_badge.setText(str(len(contacts)))

        # Créer les cartes
        for contact in contacts:
            card = ContactCard(contact, self)
            self.cards_layout.addWidget(card)

    def _on_back_clicked(self):
        """Retourne à la liste des clients."""
        if self.dashboard:
            # Navigue vers la page des clients (index 2 dans Dashboard pagesStack)
            self.dashboard._navigate_to(2, "Clients")

    def _on_toggle_sort(self):
        """Bascule le tri ascendant/descendant par objet."""
        self.sort_asc = not self.sort_asc
        self.btn_sort.setText("⇅ Trier par objet (A-Z)" if self.sort_asc else "⇅ Trier par objet (Z-A)")
        self.load_contacts()

    def _on_add_contact(self):
        """Ouvre le dialogue de création de contact pour le client courant."""
        if self.client_id is None:
            QMessageBox.warning(self, "Erreur", "Aucun client sélectionné.")
            return

        dialog = ContactDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.result_data
            try:
                self._service.create_contact(
                    client_id=self.client_id,
                    objet=data['objet'],
                    num=data['num'],
                    mail=data['mail'],
                    autres=data['autres']
                )
                self.load_contacts()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter le contact :\n{e}")

    def edit_contact(self, contact):
        """Ouvre le dialogue de modification d'un contact."""
        dialog = ContactDialog(self, contact_data=contact)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.result_data
            try:
                self._service.update_contact(
                    contact_id=contact['id'],
                    objet=data['objet'],
                    num=data['num'],
                    mail=data['mail'],
                    autres=data['autres']
                )
                self.load_contacts()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de modifier le contact :\n{e}")

    def delete_contact(self, contact):
        """Supprime un contact après confirmation."""
        reply = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer le contact pour « {contact['objet']} » ?\n"
            "Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self._service.delete_contact(contact['id'])
                self.load_contacts()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer le contact :\n{e}")
