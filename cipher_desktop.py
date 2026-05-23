"""
CIPHER SOVEREIGN — Desktop App Launcher
Starts Ollama, then the FastAPI server, then opens the
dashboard in a native Qt6 window. One double-click does everything.
"""

import sys
import os
import threading
import time
import signal
import subprocess
import urllib.request

# ── make sure we run from the script directory ──────────────
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ── Ollama location on this machine ─────────────────────────
OLLAMA_EXE = os.path.expandvars(
    r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
)
OLLAMA_URL  = "http://localhost:11434"
OLLAMA_MODEL = "deepseek-r1:8b"   # preferred model — falls back to any installed

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
    status_update = pyqtSignal(str)   # progress text
    server_ready  = pyqtSignal()
    server_failed = pyqtSignal(str)


bridge = Bridge()


# ── helpers ──────────────────────────────────────────────────
def _ollama_running() -> bool:
    try:
        urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2)
        return True
    except Exception:
        return False


def _server_running() -> bool:
    try:
        urllib.request.urlopen(f"{SERVER_URL}/status", timeout=2)
        return True
    except Exception:
        return False


# ── boot sequence (runs in background thread) ────────────────
def boot_sequence():
    """
    1. Start Ollama if not running
    2. Start FastAPI server
    3. Signal Qt when ready
    """
    # ── Step 1: Ollama ───────────────────────────────────────
    if not _ollama_running():
        bridge.status_update.emit("STARTING OLLAMA ENGINE...")
        if os.path.exists(OLLAMA_EXE):
            subprocess.Popen(
                [OLLAMA_EXE, "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW  # no extra terminal
            )
        else:
            # Fallback: try PATH
            try:
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except FileNotFoundError:
                bridge.server_failed.emit(
                    "Ollama not found. Install from https://ollama.com"
                )
                return

        # Wait up to 60s for Ollama to respond
        bridge.status_update.emit("WAITING FOR OLLAMA... (up to 60s)")
        for i in range(120):
            time.sleep(0.5)
            if _ollama_running():
                bridge.status_update.emit("OLLAMA ONLINE — LOADING MODEL...")
                break
            # Update counter every 5s so user sees progress
            if i % 10 == 0 and i > 0:
                bridge.status_update.emit(f"WAITING FOR OLLAMA... ({i//2}s)")
        else:
            bridge.server_failed.emit("Ollama started but didn't respond in 60s")
            return
    else:
        bridge.status_update.emit("OLLAMA ONLINE — STARTING CIPHER...")

    # ── Step 2: FastAPI server ───────────────────────────────
    bridge.status_update.emit("INITIALIZING CIPHER SERVER...")

    def _run_server():
        try:
            import uvicorn
            from cipher_server import app
            config = uvicorn.Config(
                app,
                host="127.0.0.1",
                port=SERVER_PORT,
                log_level="warning",
                loop="asyncio"
            )
            uvicorn.Server(config).run()
        except Exception as e:
            bridge.server_failed.emit(str(e))

    threading.Thread(target=_run_server, daemon=True).start()

    # ── Step 3: Wait for server to be ready ──────────────────
    for _ in range(60):
        time.sleep(0.5)
        if _server_running():
            bridge.status_update.emit("CIPHER SOVEREIGN ONLINE")
            bridge.server_ready.emit()
            return

    bridge.server_failed.emit("Cipher server didn't respond after 30s")


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
        bridge.status_update.connect(self._on_status_update)
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

    def _on_status_update(self, msg: str):
        self.status_lbl.setText(f"CIPHER SOVEREIGN  ·  {msg}")

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
    # Kick off full boot sequence (Ollama → FastAPI → signal Qt)
    threading.Thread(target=boot_sequence, daemon=True).start()

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
