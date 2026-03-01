"""
gui/components/outputs/outputs_page.py

Chunk: outputs_data

Shows validation results when Calculate is run.
- Error state: list of pages with missing fields, clickable to navigate
- Success state: green banner, ready for results
"""

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from gui.components.base_widget import ScrollableForm

CHUNK = "outputs_data"


class OutputsPage(ScrollableForm):

    # Emitted when user clicks a page error row — carries the page name
    navigate_requested = Signal(str)

    def __init__(self, controller=None):
        super().__init__(controller=controller, chunk_name=CHUNK)
        self._build_ui()

    def _build_ui(self):
        f = self.form

        # ── Header ────────────────────────────────────────────────────────
        header = QLabel("Outputs")
        bold = QFont()
        bold.setBold(True)
        bold.setPointSize(13)
        header.setFont(bold)
        f.addRow(header)

        # ── Calculate button ──────────────────────────────────────────────
        btn_row = QWidget()
        btn_layout = QHBoxLayout(btn_row)
        btn_layout.setContentsMargins(0, 8, 0, 8)
        btn_layout.setSpacing(10)

        self.btn_calculate = QPushButton("▶  Calculate")
        self.btn_calculate.setMinimumHeight(38)
        self.btn_calculate.setFixedWidth(160)
        self.btn_calculate.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn_layout.addWidget(self.btn_calculate)
        btn_layout.addStretch()
        f.addRow(btn_row)

        # ── Status area (swapped between states) ──────────────────────────
        self._status_widget = QWidget()
        self._status_layout = QVBoxLayout(self._status_widget)
        self._status_layout.setContentsMargins(0, 0, 0, 0)
        self._status_layout.setSpacing(0)
        f.addRow(self._status_widget)

        # Start empty
        self._show_idle()

    # ── State renderers ───────────────────────────────────────────────────────

    def _clear_status(self):
        while self._status_layout.count():
            item = self._status_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _show_idle(self):
        self._clear_status()
        note = QLabel("Press Calculate to validate all pages and run calculations.")
        note.setStyleSheet("color: gray; font-style: italic;")
        self._status_layout.addWidget(note)

    def show_errors(self, all_errors: dict):
        """
        all_errors: { "Page Name": ["Field 1", "Field 2", ...], ... }
        """
        self._clear_status()

        banner = QGroupBox()
        banner.setStyleSheet(
            "QGroupBox { border: 1px solid #ffc107; border-radius: 4px; padding: 8px; }"
        )
        banner_layout = QVBoxLayout(banner)
        banner_layout.setSpacing(4)
        bold = QFont()
        bold.setBold(True)
        title = QLabel(
            "⚠  Validation failed — please fix the following before calculating."
        )
        title.setFont(bold)
        banner_layout.addWidget(title)
        self._status_layout.addWidget(banner)
        self._status_layout.addSpacing(12)

        for page_name, errors in all_errors.items():
            card = QGroupBox()
            card.setStyleSheet(
                "QGroupBox { border: 1px solid #dee2e6; border-radius: 4px; margin-top: 0px; }"
            )
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 10, 12, 10)
            card_layout.setSpacing(6)

            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(8)

            page_label = QLabel(f"<b>{page_name}</b>")
            row_layout.addWidget(page_label)
            row_layout.addStretch()

            go_btn = QPushButton("Go to page →")
            go_btn.setFixedHeight(26)
            go_btn.setFixedWidth(110)
            go_btn.clicked.connect(
                lambda checked=False, p=page_name: self.navigate_requested.emit(p)
            )
            row_layout.addWidget(go_btn)
            card_layout.addWidget(row)

            for field in errors:
                field_label = QLabel(f"  • {field}")
                card_layout.addWidget(field_label)

            self._status_layout.addWidget(card)
            self._status_layout.addSpacing(8)

        self._status_layout.addStretch()
        self._save_state("error", all_errors)

    def show_success(self):
        self._clear_status()

        banner = QGroupBox()
        banner.setStyleSheet(
            "QGroupBox { border: 1px solid #0f5132; border-radius: 4px; padding: 8px; }"
        )
        banner_layout = QVBoxLayout(banner)
        bold = QFont()
        bold.setBold(True)
        title = QLabel("✓  All checks passed — ready to calculate.")
        title.setFont(bold)
        banner_layout.addWidget(title)
        self._status_layout.addWidget(banner)
        self._status_layout.addStretch()
        self._save_state("success", {})

    # ── Chunk persistence ─────────────────────────────────────────────────────

    def _save_state(self, status: str, errors: dict):
        if self.controller and self.controller.engine and self.chunk_name:
            self.controller.engine.stage_update(
                chunk_name=self.chunk_name,
                data={"status": status, "errors": errors},
            )

    def on_refresh(self):
        if not self.controller or not getattr(self.controller, "engine", None):
            return
        data = self.controller.engine.fetch_chunk(CHUNK) or {}
        status = data.get("status", "idle")
        if status == "error":
            self.show_errors(data.get("errors", {}))
        elif status == "success":
            self.show_success()
        else:
            self._show_idle()

    def validate(self):
        return True, []
