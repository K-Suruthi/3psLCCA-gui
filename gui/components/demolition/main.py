"""
Demolition Page Component
"""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QWidget,
)
from ..base_widget import ScrollableForm
from ..utils.form_builder.form_definitions import FieldDef, Section
from ..utils.form_builder.form_builder import build_form
from ..utils.validation_helpers import clear_field_styles, validate_form

BASE_DOCS_URL = "https://yourdocs.com/demolition/"

DEMOLITION_FIELDS = [
    Section("Demolition"),
    FieldDef(
        "demolition_disposal_cost",
        "Demolition and Disposal Cost",
        "Demolition and disposal cost expressed as a percentage of the initial construction cost.",
        "float",
        (0.0, 100.0, 2),
        "(%)",
        warn=(0.01, 40.0,
              "Demolition & Disposal Cost is 0 — cost will not be included",
              "Demolition & Disposal Cost exceeds 40% — please verify"),
    ),
    FieldDef(
        "time_required",
        "Time Required",
        "Duration required to complete the demolition works.",
        "int",
        (0, 1200),
        "(months)",
        warn=(1, 36,
              "Time Required is 0 — duration will not be included",
              "Time Required exceeds 36 months — please verify"),
    ),
    FieldDef(
        "demolition_method",
        "Demolition Method",
        "Method used to demolish the bridge structure.",
        "combo",
        ["Conventional", "Implosion", "Deconstruction"],
    ),
]


class Demolition(ScrollableForm):
    def __init__(self, controller=None):
        super().__init__(controller=controller, chunk_name="demolition_data")
        build_form(self, DEMOLITION_FIELDS, BASE_DOCS_URL)

        # Buttons Setup
        btn_row = QWidget()
        btn_layout = QHBoxLayout(btn_row)
        self.btn_load_suggested = QPushButton("Load Suggested Values")
        self.btn_clear_all = QPushButton("Clear All")
        btn_layout.addWidget(self.btn_load_suggested)
        btn_layout.addWidget(self.btn_clear_all)
        self.form.addRow(btn_row)

    def clear_validation(self):
        """Clears visual validation styles using shared helpers."""
        clear_field_styles(DEMOLITION_FIELDS, self)

    def validate(self) -> dict:
        return validate_form(DEMOLITION_FIELDS, self)

    def get_data(self) -> dict:
        """Return field values keyed by chunk name."""
        return {
            "chunk": "demolition_data",
            "data": {
                "demolition_disposal_cost": self.demolition_disposal_cost.value(),
                "time_required": self.time_required.value(),
                "demolition_method": self.demolition_method.currentText(),
            },
        }
