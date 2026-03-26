import sys
import os
from PySide6.QtWidgets import QApplication, QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit, QProxyStyle, QStyle, QTableView, QSplashScreen
from PySide6.QtCore import QObject, QEvent, Qt, QTimer
from PySide6.QtGui import QFocusEvent, QMouseEvent, QFontDatabase, QPixmap, QColor
from gui.project_manager import ProjectManager
from gui.themes import get_light_theme, get_dark_theme, resolve_is_dark, track_mode

_QSS_PATH = os.path.join("gui", "assets", "themes", "main.qss")


def _is_dark(scheme=None) -> bool:
    """Return True if the OS is in dark mode.

    Tries Qt's colorScheme enum first (Qt 6.5+); falls back to the Windows
    registry when Qt reports Unknown (common on Windows with Fusion style).
    """
    try:
        if scheme == Qt.ColorScheme.Dark:
            return True
        if scheme == Qt.ColorScheme.Light:
            return False
    except AttributeError:
        pass  # Qt.ColorScheme not available in this build

    # Windows registry fallback
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        )
        val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return val == 0
    except Exception:
        pass

    return False


def _apply_theme(scheme=None, app: QApplication = None) -> None:
    if app is None:
        app = QApplication.instance()
    is_dark = resolve_is_dark(_is_dark(scheme))
    track_mode(is_dark)
    palette, tokens = get_dark_theme() if is_dark else get_light_theme()
    app.setPalette(palette)
    if os.path.exists(_QSS_PATH):
        try:
            with open(_QSS_PATH) as f:
                qss = f.read()
            for token, value in tokens.items():
                qss = qss.replace(token, value)
            app.setStyleSheet(qss)
        except Exception as e:
            print(f"Warning: Could not reload stylesheet: {e}")



# ── Combo popup item height ───────────────────────────────────────────────────
class _ComboItemStyle(QProxyStyle):
    """Qt ignores QSS min-height on ::item in combo popups on Windows.
    This proxy enforces it at the style engine level instead."""
    _MIN_H = 36

    def sizeFromContents(self, ct, opt, sz, widget=None):
        size = super().sizeFromContents(ct, opt, sz, widget)
        if ct == QStyle.ContentsType.CT_ItemViewItem and size.height() < self._MIN_H:
            size.setHeight(self._MIN_H)
        return size


# ── Table row selection ───────────────────────────────────────────────────────
class _TableRowSelectFilter(QObject):
    """Apply single-row selection + hover highlight to every QTableView in the app.
    Uses QEvent.Polish which fires after __init__ completes, so it always wins."""
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Polish and isinstance(obj, QTableView):
            obj.setSelectionMode(QTableView.SingleSelection)
            obj.setSelectionBehavior(QTableView.SelectRows)
            obj.setMouseTracking(True)
        return super().eventFilter(obj, event)


# ── Wheel blocker ─────────────────────────────────────────────────────────────
class DisableSpinBoxScroll(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel:
            if isinstance(obj, (QSpinBox, QDoubleSpinBox, QComboBox)):
                if obj.parent():
                    QApplication.instance().sendEvent(obj.parent(), event)
                return True
        return super().eventFilter(obj, event)

# Select text when a QLineEdit is pressed
class SelectTextOnFocus(QObject):
    watching = None
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonRelease and isinstance(obj, QLineEdit):
            if self.watching != obj and obj.isEnabled():
                self.watching = obj
                obj.selectAll()
        return super().eventFilter(obj, event)


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)

    # Show splash immediately so the user sees something while loading
    _px = QPixmap(420, 140)
    _px.fill(QColor("#1a1a2e"))
    splash = QSplashScreen(_px)
    splash.showMessage(
        "Loading OS Bridge LCCA...",
        Qt.AlignHCenter | Qt.AlignBottom,
        QColor("#2ecc71"),
    )
    splash.show()
    app.processEvents()

    # Load bundled Ubuntu font family
    _font_dir = os.path.join("gui", "assets", "themes", "Ubuntu_font")
    for _ttf in [
        "Ubuntu-Light.ttf", "Ubuntu-LightItalic.ttf",
        "Ubuntu-Regular.ttf", "Ubuntu-Italic.ttf",
        "Ubuntu-Medium.ttf", "Ubuntu-MediumItalic.ttf",
        "Ubuntu-Bold.ttf", "Ubuntu-BoldItalic.ttf",
    ]:
        QFontDatabase.addApplicationFont(os.path.join(_font_dir, _ttf))

    # Load user-defined custom units after event loop starts (non-blocking)
    def _load_custom_units():
        try:
            from gui.components.utils.unit_resolver import load_custom_units
            load_custom_units()
        except Exception as _e:
            print(f"Warning: Could not load custom units: {_e}")
    QTimer.singleShot(0, _load_custom_units)

    wheel_filter = DisableSpinBoxScroll()
    app.installEventFilter(wheel_filter)

    table_filter = _TableRowSelectFilter()
    app.installEventFilter(table_filter)
    
    focus_filter = SelectTextOnFocus()
    app.installEventFilter(focus_filter)

    app.setApplicationName("OS Bridge LCCA")
    app.setOrganizationName("OSBridge")

    # Style must be set before palette/QSS — setStyle() resets the palette
    app.setStyle(_ComboItemStyle("Fusion"))
    # Apply palette + QSS for the current OS colour scheme
    _apply_theme(app.styleHints().colorScheme(), app)

    # Re-apply when the OS switches dark ↔ light at runtime (Qt 6.5+)
    try:
        app.styleHints().colorSchemeChanged.connect(lambda s: _apply_theme(s, app))
    except AttributeError:
        pass

    # First-launch: ask for user's name
    import core.start_manager as sm
    if sm.is_first_launch():
        from gui.components.first_launch_dialog import FirstLaunchDialog
        dlg = FirstLaunchDialog()
        if dlg.exec() == FirstLaunchDialog.Accepted:
            sm.set_name(dlg.get_name())
        else:
            sm.set_name("")  # mark as seen so dialog won't repeat

    manager = ProjectManager()
    splash.close()
    manager.open_project()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()