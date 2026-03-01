from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QPushButton,
    QSpinBox,
    QWidget,
)

from ..base_widget import ScrollableForm
from ..utils.form_builder.form_definitions import FieldDef, Section
from ..utils.form_builder.form_builder import build_form


BASE_DOCS_URL = "https://yourdocs.com/financial/"

FINANCIAL_FIELDS = [
    FieldDef(
        "discount_rate",
        "Discount Rate",
        "The rate used to convert future cash flows into present value. "
        "It reflects the time value of money and investment risk.",
        "float",
        options=(0.0, 100.0, 2),
        unit="(%)",
        required=True,
        doc_slug="discount-rate",
    ),
    FieldDef(
        "inflation_rate",
        "Inflation Rate",
        "Expected annual increase in general price levels over time.",
        "float",
        options=(0.0, 100.0, 2),
        unit="(%)",
        required=True,
        doc_slug="inflation-rate",
    ),
    FieldDef(
        "interest_rate",
        "Interest Rate",
        "The borrowing or lending rate applied to capital financing.",
        "float",
        options=(0.0, 100.0, 2),
        unit="(%)",
        required=True,
        doc_slug="interest-rate",
    ),
    FieldDef(
        "investment_ratio",
        "Investment Ratio",
        "Proportion of total cost financed through investment (0–1). "
        "Example: 0.5 means 50%.",
        "float",
        options=(0.0, 1.0, 4),
        required=True,
        doc_slug="investment-ratio",
    ),
    FieldDef(
        "design_life",
        "Design Life",
        "Expected operational lifetime of the system in years.",
        "int",
        options=(0, 999),
        unit="(years)",
        required=True,
        doc_slug="design-life",
    ),
    FieldDef(
        "duration_of_construction",
        "Duration of Construction",
        "Time required to complete construction before operation begins.",
        "float",
        options=(0.0, 999.0, 2),
        unit="(years)",
        doc_slug="duration-of-construction",
    ),
    FieldDef(
        "analysis_period",
        "Analysis Period",
        "Total time horizon used for financial evaluation.",
        "int",
        options=(0, 999),
        unit="(years)",
        required=True,
        doc_slug="analysis-period",
    ),
]

SUGGESTED_VALUES = {
    "discount_rate": 6.70,
    "inflation_rate": 5.15,
    "interest_rate": 7.75,
    "investment_ratio": 0.5,
    "design_life": 50,
    "duration_of_construction": 0.0,
    "analysis_period": 50,
}


class FinancialData(ScrollableForm):
    def __init__(self, controller=None):
        super().__init__(controller=controller, chunk_name="financial_data")

        self.required_keys = build_form(self, FINANCIAL_FIELDS, BASE_DOCS_URL)

        # ── Buttons row ───────────────────────────────────────────────────
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
        btn_layout.addStretch()
        self.form.addRow(btn_row)

    # ── Suggested values ──────────────────────────────────────────────────────

    def load_suggested_values(self):
        for key, val in SUGGESTED_VALUES.items():
            widget = getattr(self, key, None)
            if widget is None:
                continue
            if isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                widget.setValue(val)
            widget.setStyleSheet("")

        self._on_field_changed()

        if self.controller and self.controller.engine:
            self.controller.engine._log("Financial: Suggested values applied.")

    # ── Clear All ─────────────────────────────────────────────────────────────

    def clear_all(self):
        for entry in FINANCIAL_FIELDS:
            if isinstance(entry, Section):
                continue
            widget = getattr(self, entry.key, None)
            if widget is None:
                continue
            if isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                widget.setValue(widget.minimum())
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            widget.setStyleSheet("")

        self._on_field_changed()

        if self.controller and self.controller.engine:
            self.controller.engine._log("Financial: All fields cleared.")

    # ── Validation ────────────────────────────────────────────────────────────

    def validate(self):
        errors = []

        for key in self.required_keys:
            widget = getattr(self, key, None)
            if widget is None:
                continue
            if isinstance(widget, (QDoubleSpinBox, QSpinBox)) and widget.value() <= 0:
                label = next(
                    f.title
                    for f in FINANCIAL_FIELDS
                    if isinstance(f, FieldDef) and f.key == key
                )
                errors.append(label)
                widget.setStyleSheet("border: 1px solid red;")

        if errors:
            msg = f"Missing required financial data: {', '.join(errors)}"
            if self.controller and self.controller.engine:
                self.controller.engine._log(msg)
            return False, errors

        return True, []
