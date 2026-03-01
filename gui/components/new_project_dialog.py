# gui/components/new_project_dialog.py
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt

from .utils.countries_data import CURRENCIES, COUNTRIES


class NewProjectDialog(QDialog):
    """Collect project name, country, and currency before creating a project."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Project")
        self.setFixedWidth(420)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(24, 24, 24, 24)

        # ── Project Name ──────────────────────────────────────────────────
        layout.addWidget(QLabel("<b>Project Name</b>"))

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Highway 5 Bridge Replacement")
        self.name_input.setFixedHeight(34)
        layout.addWidget(self.name_input)

        name_hint = QLabel("You can rename this later.")
        name_hint.setEnabled(False)
        layout.addWidget(name_hint)

        layout.addSpacing(4)

        # ── Country ───────────────────────────────────────────────────────
        layout.addWidget(QLabel("<b>Country</b>"))

        self.country_input = QComboBox()
        self.country_input.setFixedHeight(34)
        self.country_input.addItem("— Select country —", "")
        for country in COUNTRIES:
            self.country_input.addItem(country, country)
        layout.addWidget(self.country_input)

        country_hint = QLabel("Cannot be changed after project creation.")
        country_hint.setEnabled(False)
        layout.addWidget(country_hint)

        layout.addSpacing(4)

        # ── Currency ──────────────────────────────────────────────────────
        layout.addWidget(QLabel("<b>Currency</b>"))

        self.currency_input = QComboBox()
        self.currency_input.setFixedHeight(34)
        self.currency_input.addItem("— Select currency —", "")
        for code in CURRENCIES:
            self.currency_input.addItem(code, code)
        layout.addWidget(self.currency_input)

        currency_hint = QLabel("Cannot be changed after project creation.")
        currency_hint.setEnabled(False)
        layout.addWidget(currency_hint)

        layout.addSpacing(8)

        # ── Buttons ───────────────────────────────────────────────────────
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self._on_accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        self.name_input.returnPressed.connect(self._on_accept)

    def _on_accept(self):
        name_ok = bool(self.name_input.text().strip())
        country_ok = bool(self.country_input.currentData())
        currency_ok = bool(self.currency_input.currentData())

        self.name_input.setStyleSheet("" if name_ok else "border: 1px solid red;")
        self.country_input.setStyleSheet("" if country_ok else "border: 1px solid red;")
        self.currency_input.setStyleSheet(
            "" if currency_ok else "border: 1px solid red;"
        )

        if name_ok and country_ok and currency_ok:
            self.accept()

    def get_name(self) -> str:
        return self.name_input.text().strip()

    def get_country(self) -> str:
        return self.country_input.currentData() or ""

    def get_currency(self) -> str:
        return self.currency_input.currentData() or ""
