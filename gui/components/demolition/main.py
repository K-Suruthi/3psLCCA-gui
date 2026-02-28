from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QWidget,
)

from ..base_widget import ScrollableForm
from ..utils.form_builder.form_definitions import FieldDef, Section
from ..utils.form_builder.form_builder import build_form


BASE_DOCS_URL = "https://yourdocs.com/demolition/"

DEMOLITION_FIELDS = [
    Section("Demolition"),
    FieldDef(
        "demolition_disposal_cost",
        "Demolition and Disposal Cost",
        "Demolition and disposal cost expressed as a percentage of the initial construction cost.",
        "float",
        options=(0.0, 100.0, 2),
        unit="(%)",
        required=True,
        doc_slug="demolition-disposal-cost",
    ),
    FieldDef(
        "time_required",
        "Time Required",
        "Duration required to complete the demolition works.",
        "int",
        options=(0, 1200),
        unit="(months)",
        required=True,
        doc_slug="demolition-time-required",
    ),
    FieldDef(
        "demolition_method",
        "Demolition Method",
        "Method used to demolish the bridge structure.",
        "combo",
        options=["Conventional", "Implosion", "Deconstruction"],
        required=True,
        doc_slug="demolition-method",
    ),
]
SUGGESTED_VALUES = {
    "demolition_method": "Conventional",
}

VALIDATION_RULES = {
    "demolition_cost": (0.0, None),
    "demolition_year": (1, 200),
    "waste_volume": (0.0, None),
    "disposal_cost": (0.0, None),
    "landfill_distance": (0.0, 500.0),
}


class Demolition(ScrollableForm):

    def __init__(self, controller=None):
        super().__init__(controller=controller, chunk_name="demolition_data")

        self.required_keys = build_form(self, DEMOLITION_FIELDS, BASE_DOCS_URL)

        # ── Buttons row ──────────────────────────────────────────────────
        btn_row = QWidget()
        btn_layout = QHBoxLayout(btn_row)
        btn_layout.setContentsMargins(0, 10, 0, 10)
        btn_layout.setSpacing(10)

        self.btn_load_suggested = QPushButton("Load Suggested Values")
        self.btn_load_suggested.setMinimumHeight(35)
        self.btn_load_suggested.clicked.connect(self.load_suggested_values)

        self.btn_clear_all = QPushButton("Clear All")
        self.btn_clear_all.setMinimumHeight(35)
        self.btn_clear_all.clicked.connect(self.clear_all)

        btn_layout.addWidget(self.btn_load_suggested)
        btn_layout.addWidget(self.btn_clear_all)
        self.form.addRow(btn_row)

    # ── Suggested values ─────────────────────────────────────────────────
    def load_suggested_values(self):
        for key, val in SUGGESTED_VALUES.items():
            widget = getattr(self, key, None)
            if widget is None:
                continue
            if isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                widget.setValue(val)
            elif isinstance(widget, QComboBox):
                idx = widget.findText(str(val))
                if idx >= 0:
                    widget.setCurrentIndex(idx)
            elif isinstance(widget, QLineEdit):
                widget.setText(str(val))
            widget.setStyleSheet("")

        self._on_field_changed()

        if self.controller and self.controller.engine:
            self.controller.engine._log("Demolition: Suggested values applied.")

    # ── Clear All ────────────────────────────────────────────────────────
    def clear_all(self):
        for entry in DEMOLITION_FIELDS:
            if isinstance(entry, Section):
                continue
            widget = getattr(self, entry.key, None)
            if widget is None:
                continue
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            elif isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                widget.setValue(widget.minimum())
            widget.setStyleSheet("")

        self._on_field_changed()

        if self.controller and self.controller.engine:
            self.controller.engine._log("Demolition: All fields cleared.")

    # ── Validation ───────────────────────────────────────────────────────
    def validate(self):
        errors = []

        for key in self.required_keys:
            widget = getattr(self, key, None)
            if widget is None:
                continue

            if isinstance(widget, QComboBox):
                continue  # always has a selection

            if isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                value = widget.value()
            elif isinstance(widget, QLineEdit):
                try:
                    value = float(widget.text())
                except ValueError:
                    errors.append(self._field_title(key))
                    widget.setStyleSheet("border: 1px solid red;")
                    continue
            else:
                continue

            min_val, max_val = VALIDATION_RULES.get(key, (0.0, None))
            if value < min_val:
                errors.append(f"{self._field_title(key)} (must be ≥ {min_val})")
                widget.setStyleSheet("border: 1px solid red;")
            elif max_val is not None and value > max_val:
                errors.append(f"{self._field_title(key)} (must be ≤ {max_val})")
                widget.setStyleSheet("border: 1px solid red;")

        if errors:
            msg = f"Invalid demolition data: {', '.join(errors)}"
            if self.controller and self.controller.engine:
                self.controller.engine._log(msg)
            return False, errors

        return True, []

    def _field_title(self, key: str) -> str:
        return next(
            (
                f.title
                for f in DEMOLITION_FIELDS
                if isinstance(f, FieldDef) and f.key == key
            ),
            key,
        )
