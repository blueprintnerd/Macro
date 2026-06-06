from qt_material_icons import MaterialIcon
import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer, QProcess, QCoreApplication
from setup import MainApp

class ServerTrayApp:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_dir, "config.json")
        self.use_gui = os.environ.get("DISPLAY") is not None
        
        if self.use_gui:
            self.app = QApplication(sys.argv)
            self.app.setQuitOnLastWindowClosed(False)
            self.setup_tray()
        else:
            self.app = QCoreApplication(sys.argv)
        
        self.api_process = None
        self.scan_process = None
        self.scan_timer = QTimer()
        self.scan_timer.setSingleShot(True)
        self.scan_timer.timeout.connect(self.run_scan)
        
        self.setup_win = None

        if not os.path.exists(self.config_path) and self.use_gui:
            self.open_setup()
        else:
            self.start_background_tasks()

    def setup_tray(self):
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon.fromTheme("system-run"))
        
        self.menu = QMenu()
        
        self.setup_action = QAction("Open Setup")
        self.setup_action.triggered.connect(self.open_setup)
        self.menu.addAction(self.setup_action)
        
        self.restart_action = QAction("Restart Server")
        self.restart_action.triggered.connect(self.restart_server)
        self.menu.addAction(self.restart_action)
        
        self.menu.addSeparator()
        
        self.exit_action = QAction("Exit")
        self.exit_action.triggered.connect(self.exit_app)
        self.menu.addAction(self.exit_action)
        
        self.tray.setContextMenu(self.menu)
        self.tray.show()

    def open_setup(self):
        if not self.use_gui:
            return
        if not self.setup_win:
            self.setup_win = MainApp()
        self.setup_win.win.show()
        self.setup_win.win.raise_()
        self.setup_win.win.activateWindow()

    def start_background_tasks(self):
        self.start_api()
        self.run_scan()

    def start_api(self):
        if self.api_process:
            self.api_process.terminate()
            self.api_process.waitForFinished(2000)
            
        api_path = os.path.join(os.path.dirname(__file__), "background", "api.py")
        if os.path.exists(api_path):
            self.api_process = QProcess()
            self.api_process.start(sys.executable, [api_path])
        
    def restart_server(self):
        self.start_api()
        self.run_scan()

    def run_scan(self):
        if self.scan_process and self.scan_process.state() == QProcess.ProcessState.Running:
            return
            
        scan_path = os.path.join(os.path.dirname(__file__), "background", "scan.py")
        if os.path.exists(scan_path):
            self.scan_process = QProcess()
            self.scan_process.finished.connect(self.schedule_next_scan)
            self.scan_process.start(sys.executable, [scan_path])
        else:
            self.schedule_next_scan()
        
    def schedule_next_scan(self):
        interval = 3600
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    interval = json.load(f).get("scan_interval", 3600)
            except:
                pass
        self.scan_timer.start(interval * 1000)

    def exit_app(self):
        if self.api_process:
            self.api_process.terminate()
            self.api_process.waitForFinished(2000)
        if self.scan_process:
            self.scan_process.terminate()
        self.app.quit()

    def run(self):
        return self.app.exec()

if __name__ == "__main__":
    tray_app = ServerTrayApp()
    sys.exit(tray_app.run())
