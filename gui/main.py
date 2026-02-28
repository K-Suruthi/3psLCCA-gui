# Directory structure:
# └── gui/
#     ├── main.py
#     ├── project_controller.py
#     ├── project_manager.py
#     ├── project_window.py
#     ├── assets/
#     │   └── themes/
#     │       └── lightstyle.qss
#     └── components/
#         ├── base_widget.py
#         ├── checkpoint_dialog.py
#         ├── home_page.py
#         ├── logs.py
#         ├── new_project_dialog.py
#         ├── recovery_dialog.py
#         ├── save_status_bar.py
#         ├── tamper_dialog.py
#         ├── bridge_data/
#         │   └── main.py
#         ├── carbon_emission/
#         │   ├── main.py
#         │   └── widgets/
#         │       ├── machinery_emissions.py
#         │       ├── material_emissions.py
#         │       ├── social_cost.py
#         │       ├── traffic_emissions.py
#         │       ├── transport_dialog.py
#         │       └── transport_emissions.py
#         ├── demolition/
#         │   └── main.py
#         ├── financial_data/
#         │   └── main.py
#         ├── global_info/
#         │   └── main.py
#         ├── maintenance/
#         │   └── main.py
#         ├── recycling/
#         │   └── main.py
#         ├── structure/
#         │   ├── excel_parser.py
#         │   ├── main.py
#         │   └── widgets/
#         │       ├── base_table.py
#         │       ├── foundation.py
#         │       ├── manager.py
#         │       ├── misc_widget.py
#         │       ├── substructure.py
#         │       ├── super_structure.py
#         │       └── trash_tab.py
#         ├── traffic_data/
#         │   └── main.py
#         └── utils/
#             ├── countries_data.py
#             ├── definitions.py
#             ├── remarks_editor.py
#             ├── unit_resolver.py
#             └── input_fields/
#                 ├── add_material.py
#                 └── config.py





import sys
import os
from PySide6.QtWidgets import QApplication, QSpinBox, QDoubleSpinBox, QComboBox
from PySide6.QtCore import QObject, QEvent
from gui.project_manager import ProjectManager


class DisableSpinBoxScroll(QObject):
    """
    Global event filter to disable mouse wheel changes
    on all QSpinBox, QDoubleSpinBox and QComboBox widgets.
    """

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel:
            if isinstance(obj, (QSpinBox, QDoubleSpinBox, QComboBox)):
                # Forward the wheel event to the parent so scroll area still scrolls
                if obj.parent():
                    QApplication.instance().sendEvent(obj.parent(), event)
                return True  # Block from the spinbox/combobox itself
        return super().eventFilter(obj, event)


def main():
    """
    Main entry point for the OS Bridge LCCA application.
    Initializes the QApplication and delegates window management to ProjectManager.
    """

    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_SCALE_FACTOR"] = "1.1"  # try 1.1 – 1.3

    app = QApplication(sys.argv)

    # Install global wheel blocker
    wheel_filter = DisableSpinBoxScroll()
    app.installEventFilter(wheel_filter)

    # Optional: Set Application Name for OS-level identification
    app.setApplicationName("OS Bridge LCCA")
    app.setOrganizationName("OSBridge")

    # Optional: Load the QSS theme if available
    qss_path = os.path.join("gui", "assets", "themes", "lightstyle.qss")
    if os.path.exists(qss_path):
        try:
            with open(qss_path, "r") as f:
                app.setStyleSheet(f.read())
        except Exception as e:
            print(f"Warning: Could not load stylesheet: {e}")

    # Initialize the Manager
    manager = ProjectManager()
    manager.open_project()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
