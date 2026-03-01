import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QAction, QColor

from gui.components.save_status_bar import SaveStatusBar
from gui.components.logs import Logs
from gui.components.global_info.main import GeneralInfo
from gui.components.bridge_data.main import BridgeData
from gui.components.structure.main import StructureTabView
from gui.components.traffic_data.main import TrafficData
from gui.components.financial_data.main import FinancialData
from gui.components.carbon_emission.main import CarbonEmissionTabView
from gui.components.maintenance.main import Maintenance
from gui.components.recycling.main import Recycling
from gui.components.demolition.main import Demolition
from gui.components.home_page import HomePage
from gui.components.outputs.outputs_page import OutputsPage


# ── Sidebar tree definition ───────────────────────────────────────────────────

SIDEBAR_TREE = {
    "General Information": {},
    "Bridge Data": {},
    "Input Parameters": {
        "Construction Work Data": [
            "Foundation",
            "Super Structure",
            "Sub Structure",
            "Miscellaneous",
        ],
        "Traffic Data": [],
        "Financial Data": [],
        "Carbon Emission Data": [
            "Material Emissions",
            "Transportation Emissions",
            "Machinery Emissions",
            "Traffic Diversion Emissions",
            "Social Cost of Carbon",
        ],
        "Maintenance and Repair": [],
        "Recycling": [],
        "Demolition": [],
    },
    "Outputs": {},
}


# ── Main window ───────────────────────────────────────────────────────────────


class ProjectWindow(QMainWindow):
    def __init__(self, manager, controller=None):
        super().__init__()
        self.manager = manager

        if controller is not None:
            self.controller = controller
        else:
            from gui.project_controller import ProjectController

            self.controller = ProjectController()

        self.project_id = None

        self.setWindowTitle("LCCA - Home")
        self.resize(1100, 750)

        self.main_stack = QStackedWidget()
        self.setCentralWidget(self.main_stack)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self._setup_home_ui()  # index 0
        self._setup_project_ui()  # index 1

        # ── Controller signals ────────────────────────────────────────────
        self.controller.fault_occurred.connect(self._on_fault)
        self.controller.project_loaded.connect(self._on_project_loaded)
        self.controller.sync_completed.connect(
            lambda: self.status_bar.showMessage("All changes saved.", 3000)
        )
        self.controller.dirty_changed.connect(
            lambda d: self.status_bar.showMessage("Unsaved changes...") if d else None
        )

        self.show_home()

    # ── Home screen ───────────────────────────────────────────────────────────

    def _setup_home_ui(self):
        self.home_widget = HomePage(manager=self.manager)
        self.main_stack.addWidget(self.home_widget)  # index 0

    # ── Project view ──────────────────────────────────────────────────────────

    def _setup_project_ui(self):
        self.project_widget = QWidget()
        master_layout = QVBoxLayout(self.project_widget)
        master_layout.setContentsMargins(0, 0, 0, 0)
        master_layout.setSpacing(0)

        # ── Top bar ───────────────────────────────────────────────────────
        top_bar = QWidget()
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(8, 4, 8, 4)
        top_bar_layout.setSpacing(8)

        self.menubar = QMenuBar()

        self.menuFile = QMenu("&File", self.menubar)
        for label in ["New", "Open"]:
            self.menuFile.addAction(QAction(label, self))
        self.menuFile.addSeparator()
        self.actionSave = QAction("Save", self)
        self.menuFile.addAction(self.actionSave)
        for label in ["Save As...", "Create a Copy", "Print"]:
            self.menuFile.addAction(QAction(label, self))
        self.menuFile.addSeparator()
        for label in ["Rename", "Export", "Version History", "Info"]:
            self.menuFile.addAction(QAction(label, self))

        self.menuHelp = QMenu("&Help", self.menubar)
        for label in ["Contact us", "Feedback"]:
            self.menuHelp.addAction(QAction(label, self))
        self.menuHelp.addSeparator()
        for label in ["Video Tutorials", "Join our Community"]:
            self.menuHelp.addAction(QAction(label, self))

        home_action = QAction("Home", self)
        home_action.triggered.connect(self.show_home)

        self.log_action = QAction("Logs", self)

        self.menubar.addAction(home_action)
        self.menubar.addMenu(self.menuFile)
        self.menubar.addMenu(self.menuHelp)
        self.menubar.addAction(QAction("Tutorials", self))
        self.menubar.addAction(self.log_action)

        top_bar_layout.addWidget(self.menubar)
        top_bar_layout.addStretch()
        self.save_status_bar = SaveStatusBar(controller=self.controller)
        top_bar_layout.addWidget(self.save_status_bar)

        self.btn_calculate = QPushButton("Calculate")
        self.btn_calculate.clicked.connect(self._run_calculate)
        top_bar_layout.addWidget(self.btn_calculate)
        top_bar_layout.addWidget(QPushButton("Lock"))

        master_layout.setMenuBar(top_bar)

        # ── Sidebar ───────────────────────────────────────────────────────
        self.sidebar = QTreeWidget()
        self.sidebar.setHeaderHidden(True)
        self.sidebar.setMinimumWidth(80)
        self.sidebar.setContentsMargins(4, 4, 4, 4)
        self.sidebar.setStyleSheet("QTreeWidget { padding: 4px; }")

        for header, subheaders in SIDEBAR_TREE.items():
            top_item = QTreeWidgetItem(self.sidebar)
            top_item.setText(0, header)
            for subheader, subitems in subheaders.items():
                sub_item = QTreeWidgetItem(top_item)
                sub_item.setText(0, subheader)
                for subitem in subitems:
                    leaf = QTreeWidgetItem(sub_item)
                    leaf.setText(0, subitem)

        self.sidebar.expandAll()
        self.sidebar.itemPressed.connect(self._select_sidebar)

        # ── Content stack ─────────────────────────────────────────────────
        self.content_stack = QStackedWidget()

        self.metadata_page = QLabel()
        self.metadata_page.setAlignment(Qt.AlignCenter)

        self.logs_page = Logs(controller=self.controller)

        self.outputs_page = OutputsPage(controller=self.controller)
        self.outputs_page.navigate_requested.connect(self._navigate_to_page)
        self.outputs_page.btn_calculate.clicked.connect(self._run_calculate)

        self.widget_map = {
            "General Information": GeneralInfo(controller=self.controller),
            "Bridge Data": BridgeData(controller=self.controller),
            "Construction Work Data": StructureTabView(controller=self.controller),
            "Traffic Data": TrafficData(controller=self.controller),
            "Financial Data": FinancialData(controller=self.controller),
            "Carbon Emission Data": CarbonEmissionTabView(controller=self.controller),
            "Maintenance and Repair": Maintenance(controller=self.controller),
            "Recycling": Recycling(controller=self.controller),
            "Demolition": Demolition(controller=self.controller),
            "Outputs": self.outputs_page,
        }

        for widget in self.widget_map.values():
            self.content_stack.addWidget(widget)
        self.content_stack.addWidget(self.logs_page)

        self.log_action.triggered.connect(
            lambda: self.content_stack.setCurrentWidget(self.logs_page)
        )

        # ── Splitter ──────────────────────────────────────────────────────
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.content_stack)
        self.splitter.setSizes([220, 880])

        master_layout.addWidget(self.splitter, stretch=1)
        self.main_stack.addWidget(self.project_widget)  # index 1

    def _select_sidebar(self, item: QTreeWidgetItem):
        header = item.text(0)
        parent = item.parent()
        item.setExpanded(True)

        if header in self.widget_map:
            self.content_stack.setCurrentWidget(self.widget_map[header])
            return

        if parent is None:
            return

        parent_header = parent.text(0)

        if parent_header == "Construction Work Data":
            self.content_stack.setCurrentWidget(
                self.widget_map["Construction Work Data"]
            )
            self.widget_map["Construction Work Data"].select_tab(header)

        elif parent_header == "Carbon Emission Data":
            self.content_stack.setCurrentWidget(self.widget_map["Carbon Emission Data"])
            self.widget_map["Carbon Emission Data"].select_tab(header)

    # ── View switching ────────────────────────────────────────────────────────

    def show_home(self):
        self.setWindowTitle("LCCA - Home")
        self.home_widget.set_active_project(
            self.project_id if self.has_project_loaded() else None
        )
        self.home_widget.refresh_project_list()
        self.main_stack.setCurrentWidget(self.home_widget)
        self.manager.refresh_all_home_screens()

    def show_project_view(self):
        if not self.has_project_loaded():
            return
        display = self.controller.active_display_name or self.project_id
        self.setWindowTitle(f"LCCA - {display}")
        self.main_stack.setCurrentWidget(self.project_widget)
        self.content_stack.setCurrentWidget(self.widget_map["General Information"])
        items = self.sidebar.findItems("General Information", Qt.MatchExactly)
        if items:
            self.sidebar.setCurrentItem(items[0])

    def has_project_loaded(self):
        return self.project_id is not None

    # ── Calculate ─────────────────────────────────────────────────────────────

    def _run_calculate(self):
        all_errors = {}
        validation_results = {}  # name -> (has_real_validation, ok)

        for name, widget in self.widget_map.items():
            if name == "Outputs":
                continue
            if not hasattr(widget, "validate"):
                continue
            ok, errors = widget.validate()
            # Distinguish real validation from stub (return True, [])
            # A stub always returns True with empty errors — we detect real
            # validation by checking if required_keys exists and is non-empty
            has_real_validation = bool(getattr(widget, "required_keys", None))
            validation_results[name] = (has_real_validation, ok)
            if not ok and errors:
                all_errors[name] = errors

        self._update_sidebar_colors(validation_results)

        # Navigate to outputs page
        self.content_stack.setCurrentWidget(self.outputs_page)
        items = self.sidebar.findItems("Outputs", Qt.MatchExactly)
        if items:
            self.sidebar.setCurrentItem(items[0])

        if all_errors:
            self.outputs_page.show_errors(all_errors)
        else:
            self.outputs_page.show_success()

    def _update_sidebar_colors(self, validation_results: dict):
        """Color sidebar items: red = fail, default = everything else."""
        RED = QColor("#c0392b")

        for name, (has_real_validation, ok) in validation_results.items():
            items = self.sidebar.findItems(name, Qt.MatchExactly | Qt.MatchRecursive)
            for item in items:
                if has_real_validation and not ok:
                    item.setForeground(0, RED)
                else:
                    item.setForeground(0, self.sidebar.palette().text())

    def _navigate_to_page(self, page_name: str):
        """Navigate sidebar + content stack to a named page."""
        widget = self.widget_map.get(page_name)
        if widget:
            self.content_stack.setCurrentWidget(widget)
        items = self.sidebar.findItems(page_name, Qt.MatchExactly | Qt.MatchRecursive)
        if items:
            self.sidebar.setCurrentItem(items[0])

    # ── Controller signals ────────────────────────────────────────────────────

    def _on_project_loaded(self):
        if not self.controller.active_project_id:
            return
        self.project_id = self.controller.active_project_id
        display = self.controller.active_display_name or self.project_id
        self.setWindowTitle(f"LCCA - {display}")
        self.status_bar.showMessage(f"Project: {display}")
        self.show_project_view()

    def _on_fault(self, error_message: str):
        QMessageBox.critical(
            self,
            "Engine Error — Data may not be saved",
            f"A critical storage error occurred:\n\n{error_message}\n\n"
            "Save a checkpoint immediately if possible, then restart.",
        )

    # ── Close ─────────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        if self.controller.engine:
            self.controller.close_project()
        self.project_id = None
        self.manager.remove_window(self)
        self.manager.refresh_all_home_screens()
        event.accept()
