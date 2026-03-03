"""
gui/components/maintenance/main.py
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


BASE_DOCS_URL = "https://yourdocs.com/maintenance/"

MAINTENANCE_FIELDS = [
    # ── Routine Maintenance ──────────────────────────────────────────────
    Section("Routine Maintenance"),
    FieldDef(
        "routine_inspection_cost",
        "Routine Inspection Cost",
        "Cost of routine inspection expressed as a percentage of initial construction cost.",
        "float",
        options=(0.0, 100.0, 2),
        unit="(%)",
        required=True,
        doc_slug="routine-inspection-cost",
        warn=(0.01, 100.0, "Routine Inspection Cost is 0 — cost will not be included"),
    ),
    FieldDef(
        "routine_inspection_freq",
        "Routine Inspection Frequency",
        "Interval between routine inspections.",
        "int",
        options=(0, 50),
        unit="(yr)",
        required=True,
        doc_slug="routine-inspection-freq",
        warn=(1, 50, "Routine Inspection Frequency seems unusual — expected between 1 and 50 years"),
    ),
    # ── Periodic Maintenance ─────────────────────────────────────────────
    Section("Periodic Maintenance"),
    FieldDef(
        "periodic_maintenance_cost",
        "Periodic Maintenance Cost",
        "Cost of periodic maintenance expressed as a percentage of initial construction cost.",
        "float",
        options=(0.0, 100.0, 1),
        unit="(%)",
        required=True,
        doc_slug="periodic-maintenance-cost",
        warn=(0.01, 100.0, "Periodic Maintenance Cost is 0 — cost will not be included"),
    ),
    FieldDef(
        "periodic_maintenance_freq",
        "Periodic Maintenance Frequency",
        "Interval between periodic maintenance works.",
        "int",
        options=(0, 100),
        unit="(yr)",
        required=True,
        doc_slug="periodic-maintenance-freq",
        warn=(1, 100, "Periodic Maintenance Frequency seems unusual — expected between 1 and 100 years"),
    ),
    # ── Major Works ──────────────────────────────────────────────────────
    Section("Major Works"),
    FieldDef(
        "major_inspection_cost",
        "Major Inspection Cost",
        "Cost of major inspection expressed as a percentage of initial construction cost.",
        "float",
        options=(0.0, 100.0, 2),
        unit="(%)",
        required=True,
        doc_slug="major-inspection-cost",
        warn=(0.01, 100.0, "Major Inspection Cost is 0 — cost will not be included"),
    ),
    FieldDef(
        "major_inspection_freq",
        "Major Inspection Frequency",
        "Interval between major inspections.",
        "int",
        options=(0, 100),
        unit="(yr)",
        required=True,
        doc_slug="major-inspection-freq",
        warn=(1, 100, "Major Inspection Frequency seems unusual — expected between 1 and 100 years"),
    ),
    FieldDef(
        "major_repair_cost",
        "Major Repair Cost",
        "Cost of major repair expressed as a percentage of initial construction cost.",
        "float",
        options=(0.0, 100.0, 1),
        unit="(%)",
        required=True,
        doc_slug="major-repair-cost",
        warn=(0.01, 100.0, "Major Repair Cost is 0 — cost will not be included"),
    ),
    FieldDef(
        "major_repair_freq",
        "Major Repair Frequency",
        "Interval between major repair works.",
        "int",
        options=(0, 100),
        unit="(yr)",
        required=True,
        doc_slug="major-repair-freq",
        warn=(1, 100, "Major Repair Frequency seems unusual — expected between 1 and 100 years"),
    ),
    # ── Bearings & Expansion Joints ──────────────────────────────────────
    Section("Bearings & Expansion Joints"),
    FieldDef(
        "bearing_exp_joint_cost",
        "Bearing & Expansion Joint Repair Cost",
        "Cost of bearing and expansion joint repair expressed as a percentage of initial construction cost.",
        "float",
        options=(0.0, 100.0, 2),
        unit="(%)",
        required=True,
        doc_slug="bearing-exp-joint-cost",
        warn=(0.01, 100.0, "Bearing & Expansion Joint Cost is 0 — cost will not be included"),
    ),
    FieldDef(
        "bearing_exp_joint_freq",
        "Bearing & Expansion Joint Repair Frequency",
        "Interval between bearing and expansion joint repair works.",
        "int",
        options=(0, 100),
        unit="(yr)",
        required=True,
        doc_slug="bearing-exp-joint-freq",
        warn=(1, 100, "Bearing & Expansion Joint Frequency seems unusual — expected between 1 and 100 years"),
    ),
    # ── Strategy ─────────────────────────────────────────────────────────
    Section("Strategy"),
    FieldDef(
        "maintenance_strategy",
        "Maintenance Strategy",
        "Overall maintenance approach applied over the bridge service life.",
        "combo",
        options=["Corrective", "Preventive", "Condition-based"],
        required=True,
        doc_slug="maintenance-strategy",
    ),
]

SUGGESTED_VALUES = {
    "routine_inspection_freq": 1,
    "periodic_maintenance_freq": 5,
    "major_inspection_freq": 10,
    "major_repair_freq": 20,
    "bearing_exp_joint_freq": 20,
    "maintenance_strategy": "Preventive",
}



class Maintenance(ScrollableForm):

    def __init__(self, controller=None):
        super().__init__(controller=controller, chunk_name="maintenance_data")

        self.required_keys = build_form(self, MAINTENANCE_FIELDS, BASE_DOCS_URL)

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
            self.controller.engine._log("Maintenance: Suggested values applied.")

    # ── Clear All ────────────────────────────────────────────────────────
    def clear_all(self):
        for entry in MAINTENANCE_FIELDS:
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
            self.controller.engine._log("Maintenance: All fields cleared.")

    # ── Validation ───────────────────────────────────────────────────────
    def clear_validation(self):
        clear_field_styles(MAINTENANCE_FIELDS, self)

    def validate(self) -> dict:
        return validate_form(MAINTENANCE_FIELDS, self)

    def get_data(self) -> dict:
        return {"chunk": "maintenance_data", "data": self.get_data_dict()}

