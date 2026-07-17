from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QCheckBox, QPushButton, QMessageBox, 
    QHeaderView, QStyle, QStyleOptionButton
)
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QObject


class CheckBoxHeader(QHeaderView):
    """Custom table header with a selectable checkbox in the first section."""
    checkbox_toggled = pyqtSignal(bool)

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.isOn = False

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        super().paintSection(painter, rect, logicalIndex)
        painter.restore()

        if logicalIndex == 0:
            option = QStyleOptionButton()
            cb_size = 16
            x = rect.x() + (rect.width() - cb_size) // 2
            y = rect.y() + (rect.height() - cb_size) // 2
            option.rect = QRect(x, y, cb_size, cb_size)
            option.state = QStyle.State_Enabled | QStyle.State_Active
            if self.isOn:
                option.state |= QStyle.State_On
            else:
                option.state |= QStyle.State_Off
            self.style().drawControl(QStyle.CE_CheckBox, option, painter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            index = self.logicalIndexAt(event.pos())
            if index == 0:
                self.isOn = not self.isOn
                self.updateSection(0)
                self.checkbox_toggled.emit(self.isOn)
                return
        super().mousePressEvent(event)

    def setChecked(self, checked):
        if self.isOn != checked:
            self.isOn = checked
            self.updateSection(0)


class BulkDeleteHelper(QObject):
    """Reusable helper to handle bulk delete functionality on QTableWidget.
    
    It injects a checkbox column at index 0, creates a bulk delete button, 
    manages selection across pages, and transparently shifts column accesses 
    by monkey-patching setItem and setCellWidget.
    """

    def __init__(self, table, header_layout, delete_callback, refresh_callback, item_name_plural="éléments", parent=None):
        super().__init__(parent)
        self.table = table
        self.delete_callback = delete_callback
        self.refresh_callback = refresh_callback
        self.item_name_plural = item_name_plural
        self.selected_ids = set()
        self.checkboxes = {}  # maps row_idx to (checkbox_widget, item_id)

        # ── 1. Snapshot the original header config BEFORE changing anything ──
        original_col_count = self.table.columnCount()
        old_header = self.table.horizontalHeader()

        # Read labels
        old_labels = []
        for i in range(original_col_count):
            item = self.table.horizontalHeaderItem(i)
            old_labels.append(item.text() if item else "")

        # Read resize modes and fixed sizes
        resize_modes = []
        fixed_sizes = {}
        for i in range(original_col_count):
            mode = old_header.sectionResizeMode(i)
            resize_modes.append(mode)
            if mode in (QHeaderView.Fixed, QHeaderView.Interactive):
                fixed_sizes[i] = old_header.sectionSize(i)

        had_sort_indicator = old_header.isSortIndicatorShown()
        was_clickable = old_header.sectionsClickable()

        # ── 2. Add the extra checkbox column ─────────────────────────────────
        self.table.setColumnCount(original_col_count + 1)
        new_labels = [""] + old_labels
        self.table.setHorizontalHeaderLabels(new_labels)

        # ── 3. Create and install the custom header ──────────────────────────
        self.custom_header = CheckBoxHeader(Qt.Horizontal, self.table)
        self.table.setHorizontalHeader(self.custom_header)

        # Configure header properties
        self.custom_header.setSortIndicatorShown(had_sort_indicator)
        self.custom_header.setSectionsClickable(was_clickable)

        # Checkbox column: fixed narrow width
        self.custom_header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.custom_header.resizeSection(0, 40)

        # Copy original resize modes shifted by +1
        for i, mode in enumerate(resize_modes):
            self.custom_header.setSectionResizeMode(i + 1, mode)
            if i in fixed_sizes:
                self.custom_header.resizeSection(i + 1, fixed_sizes[i])

        # Connect signals
        self.custom_header.checkbox_toggled.connect(self._on_header_checkbox_clicked)

        if hasattr(parent, '_on_header_clicked'):
            self.custom_header.sectionClicked.connect(self._on_section_clicked_wrapper)

        # ── 4. Create the bulk delete button ─────────────────────────────────
        self.btn_bulk_delete = QPushButton("Supprimer la sélection")
        self.btn_bulk_delete.setFixedHeight(42)
        self.btn_bulk_delete.setCursor(Qt.PointingHandCursor)
        self.btn_bulk_delete.setStyleSheet("""
            QPushButton {
                background-color: #fff5f5;
                color: #d32f2f;
                border: 1px solid #ffcdd2;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #ffebee;
                border-color: #ef5350;
            }
            QPushButton:disabled {
                background-color: #f5f5f5;
                color: #cbd5e1;
                border-color: #e2e8f0;
            }
        """)
        self.btn_bulk_delete.setEnabled(False)
        self.btn_bulk_delete.clicked.connect(self._on_bulk_delete_clicked)

        # Insert before the last widget (the "Add" button)
        count = header_layout.count()
        if count > 0:
            header_layout.insertWidget(count - 1, self.btn_bulk_delete)
        else:
            header_layout.addWidget(self.btn_bulk_delete)

        # ── 5. Monkey-patch table methods to shift column indices by +1 ──────
        self.original_setItem = self.table.setItem
        self.original_setCellWidget = self.table.setCellWidget
        self.original_setRowCount = self.table.setRowCount

        self.table.setItem = self._custom_setItem
        self.table.setCellWidget = self._custom_setCellWidget
        self.table.setRowCount = self._custom_setRowCount

        # Monkey-patch setSortIndicator on custom header to shift by +1
        self.original_setSortIndicator = self.custom_header.setSortIndicator
        self.custom_header.setSortIndicator = self._custom_setSortIndicator

    # ── Monkey-patched methods ───────────────────────────────────────────────

    def _custom_setItem(self, row, column, item):
        self.original_setItem(row, column + 1, item)

    def _custom_setCellWidget(self, row, column, widget):
        self.original_setCellWidget(row, column + 1, widget)

    def _custom_setRowCount(self, count):
        self.checkboxes.clear()
        self.original_setRowCount(count)
        if count == 0:
            self._update_header_checkbox_state()
            self._update_button_state()

    def _custom_setSortIndicator(self, logicalIndex, order):
        self.original_setSortIndicator(logicalIndex + 1, order)

    # ── Signal handlers ──────────────────────────────────────────────────────

    def _on_section_clicked_wrapper(self, column_idx):
        if column_idx == 0:
            return  # Column 0 is the checkbox, not sortable
        if hasattr(self.parent(), '_on_header_clicked'):
            self.parent()._on_header_clicked(column_idx - 1)

    def _on_bulk_delete_clicked(self):
        """Triggered when the bulk delete button is clicked."""
        count = len(self.selected_ids)
        if count == 0:
            return

        reply = QMessageBox.question(
            self.table,
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer {count} {self.item_name_plural} ?\n"
            "Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            ids_to_delete = list(self.selected_ids)
            try:
                self.delete_callback(ids_to_delete)
                self.selected_ids.clear()
                self.custom_header.setChecked(False)
                self._update_button_state()
                self.refresh_callback()
            except Exception as e:
                QMessageBox.critical(
                    self.table,
                    "Erreur",
                    f"Impossible de supprimer les {self.item_name_plural} :\n{e}"
                )

    # ── Public API ───────────────────────────────────────────────────────────

    def clear_selection(self):
        self.selected_ids.clear()
        self.custom_header.setChecked(False)
        self._update_button_state()
        self._update_row_checkboxes_visuals()

    def add_row_checkbox(self, row_idx, item_id):
        """Add a checkbox at column 0 for the given row."""
        container = QWidget()
        layout = QHBoxLayout(container)
        checkbox = QCheckBox()
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        checkbox.setStyleSheet("""
            QCheckBox {
                background: transparent;
            }
        """)

        # Set checkbox state without triggering signals
        checkbox.blockSignals(True)
        checkbox.setChecked(item_id in self.selected_ids)
        checkbox.blockSignals(False)

        # Store ref
        self.checkboxes[row_idx] = (checkbox, item_id)

        # Connect state change
        checkbox.stateChanged.connect(
            lambda state, i_id=item_id: self._on_row_checkbox_changed(state, i_id)
        )

        # Set cell widget at real column 0 (bypass the monkey-patch shift)
        self.original_setCellWidget(row_idx, 0, container)

        # After the last row, sync header checkbox and button
        if row_idx == self.table.rowCount() - 1:
            self._update_header_checkbox_state()
            self._update_button_state()

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _on_row_checkbox_changed(self, state, item_id):
        if state == Qt.Checked:
            self.selected_ids.add(item_id)
        else:
            self.selected_ids.discard(item_id)

        self._update_header_checkbox_state()
        self._update_button_state()

    def _on_header_checkbox_clicked(self, checked):
        if self.table.rowCount() == 0:
            self.custom_header.setChecked(False)
            return

        for row_idx in range(self.table.rowCount()):
            if row_idx in self.checkboxes:
                checkbox, item_id = self.checkboxes[row_idx]
                checkbox.blockSignals(True)
                checkbox.setChecked(checked)
                checkbox.blockSignals(False)

                if checked:
                    self.selected_ids.add(item_id)
                else:
                    self.selected_ids.discard(item_id)

        self._update_button_state()

    def _update_header_checkbox_state(self):
        if not self.checkboxes:
            self.custom_header.setChecked(False)
            return

        all_checked = all(cb.isChecked() for cb, _ in self.checkboxes.values())
        self.custom_header.setChecked(all_checked)

    def _update_button_state(self):
        count = len(self.selected_ids)
        if count > 0:
            self.btn_bulk_delete.setText(f"Supprimer la sélection ({count})")
            self.btn_bulk_delete.setEnabled(True)
        else:
            self.btn_bulk_delete.setText("Supprimer la sélection")
            self.btn_bulk_delete.setEnabled(False)

    def _update_row_checkboxes_visuals(self):
        for checkbox, item_id in self.checkboxes.values():
            checkbox.blockSignals(True)
            checkbox.setChecked(item_id in self.selected_ids)
            checkbox.blockSignals(False)
