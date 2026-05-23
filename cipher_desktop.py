"""
CIPHER SOVEREIGN — Desktop App Launcher
Starts the FastAPI server in a background thread, then opens
the dashboard in a native Qt6 window. No browser required.
"""

import sys
import os
import threading
import time
import signal

# ── make sure we run from the script directory ──────────────
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage
from PyQt6.QtCore import QUrl, Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QColor, QPalette

SERVER_URL = "http://localhost:3131"
SERVER_PORT = 3131


# ── signals bridge (thread → Qt) ────────────────────────────
class Bridge(QObject):
    server_ready = pyqtSignal()
    server_failed = pyqtSignal(str)


bridge = Bridge()


# ── start FastAPI server in background thread ────────────────
def start_server():
    """Boot the FastAPI server. Signals when ready."""
    try:
        import uvicorn
        from cipher_server import app
        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=SERVER_PORT,
            log_level="warning",   # quiet — errors only
            loop="asyncio"
        )
        server = uvicorn.Server(config)

        # Poll until bound, then signal Qt
        def _watch():
            for _ in range(40):          # up to 20s
                time.sleep(0.5)
                try:
                    import urllib.request
                    urllib.request.urlopen(f"{SERVER_URL}/status", timeout=2)
                    bridge.server_ready.emit()
                    return
                except Exception:
                    pass
            bridge.server_failed.emit("Server didn't respond after 20s")

        threading.Thread(target=_watch, daemon=True).start()
        server.run()

    except Exception as e:
        bridge.server_failed.emit(str(e))


# ── custom web page (suppress JS console noise) ─────────────
class SilentPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        pass   # swallow — keep terminal clean


# ── main window ─────────────────────────────────────────────
class CipherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CIPHER SOVEREIGN  ·  COAI")
        self.setMinimumSize(1100, 700)
        self.resize(1400, 900)
        self._apply_dark_frame()

        # ── central widget ───────────────────────────────────
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── loading bar (shown while server boots) ───────────
        self.loading_bar = QWidget()
        self.loading_bar.setFixedHeight(48)
        self.loading_bar.setStyleSheet(
            "background:#04111F; border-bottom:1px solid #1A3A55;"
        )
        lb_layout = QHBoxLayout(self.loading_bar)
        lb_layout.setContentsMargins(20, 0, 20, 0)

        hex_lbl = QLabel("⬡")
        hex_lbl.setStyleSheet("color:#CC2936; font-size:20px;")
        lb_layout.addWidget(hex_lbl)

        self.status_lbl = QLabel("CIPHER SOVEREIGN  ·  INITIALIZING...")
        self.status_lbl.setStyleSheet(
            "color:#B8D4E8; font-family:monospace; font-size:12px; letter-spacing:2px;"
        )
        lb_layout.addWidget(self.status_lbl)
        lb_layout.addStretch()

        self.dot_lbl = QLabel("●")
        self.dot_lbl.setStyleSheet("color:#C9A84C; font-size:14px;")
        lb_layout.addWidget(self.dot_lbl)

        layout.addWidget(self.loading_bar)

        # ── web view ─────────────────────────────────────────
        self.browser = QWebEngineView()
        self.browser.setPage(SilentPage(self.browser))
        self._configure_browser()
        self.browser.hide()
        layout.addWidget(self.browser)

        # ── dot blink timer ──────────────────────────────────
        self._blink = False
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self._blink_dot)
        self.blink_timer.start(600)

        # ── connect server signals ───────────────────────────
        bridge.server_ready.connect(self._on_server_ready)
        bridge.server_failed.connect(self._on_server_failed)

    def _apply_dark_frame(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window,      QColor("#04111F"))
        palette.setColor(QPalette.ColorRole.WindowText,  QColor("#B8D4E8"))
        palette.setColor(QPalette.ColorRole.Base,        QColor("#081929"))
        palette.setColor(QPalette.ColorRole.Text,        QColor("#B8D4E8"))
        self.setPalette(palette)

    def _configure_browser(self):
        settings = self.browser.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled,           True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled,         True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled,       True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled,              False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows,    False)

    def _blink_dot(self):
        self._blink = not self._blink
        self.dot_lbl.setStyleSheet(
            f"color:{'#C9A84C' if self._blink else '#1A3A55'}; font-size:14px;"
        )

    def _on_server_ready(self):
        self.blink_timer.stop()
        self.dot_lbl.setStyleSheet("color:#0FC070; font-size:14px;")
        self.status_lbl.setText("CIPHER SOVEREIGN  ·  ONLINE")
        self.status_lbl.setStyleSheet(
            "color:#0FC070; font-family:monospace; font-size:12px; letter-spacing:2px;"
        )

        # small delay so server is fully warm before loading
        QTimer.singleShot(300, self._load_dashboard)

    def _load_dashboard(self):
        self.browser.load(QUrl(SERVER_URL))
        self.browser.loadFinished.connect(self._on_load_finished)

    def _on_load_finished(self, ok):
        if ok:
            self.loading_bar.hide()
            self.browser.show()

    def _on_server_failed(self, error):
        self.blink_timer.stop()
        self.dot_lbl.setStyleSheet("color:#FF3D4A; font-size:14px;")
        self.status_lbl.setText(f"STARTUP FAILED: {error}")
        self.status_lbl.setStyleSheet(
            "color:#FF3D4A; font-family:monospace; font-size:11px;"
        )

    def closeEvent(self, event):
        """Kill the server process when the window closes."""
        os.kill(os.getpid(), signal.SIGTERM)
        event.accept()


# ── entry point ──────────────────────────────────────────────
def main():
    # Start server in background before Qt starts
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    app = QApplication(sys.argv)
    app.setApplicationName("Cipher Sovereign")
    app.setOrganizationName("COAI")

    # App-wide dark style polish
    app.setStyle("Fusion")
    dark = QPalette()
    dark.setColor(QPalette.ColorRole.Window,          QColor("#04111F"))
    dark.setColor(QPalette.ColorRole.WindowText,      QColor("#B8D4E8"))
    dark.setColor(QPalette.ColorRole.Base,            QColor("#081929"))
    dark.setColor(QPalette.ColorRole.AlternateBase,   QColor("#0D2137"))
    dark.setColor(QPalette.ColorRole.Text,            QColor("#B8D4E8"))
    dark.setColor(QPalette.ColorRole.Button,          QColor("#0D2137"))
    dark.setColor(QPalette.ColorRole.ButtonText,      QColor("#B8D4E8"))
    dark.setColor(QPalette.ColorRole.Highlight,       QColor("#CC2936"))
    dark.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(dark)

    window = CipherWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
