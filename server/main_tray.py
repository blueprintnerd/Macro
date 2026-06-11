import sys
import os
import json
import sqlite3

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from background.sqlite import create_connection, setup_database
from tui_setup import run_tui_setup

def is_setup_complete():
    # Ensure the database and tables exist.
    setup_database()
    
    conn = create_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users")
        if cursor.fetchone() is None:
            return False
        cursor.execute("SELECT 1 FROM config WHERE key = 'paths'")
        if cursor.fetchone() is None:
            return False
        return True
    finally:
        conn.close()


def main():
    use_gui = os.environ.get("DISPLAY") is not None

    if not is_setup_complete():
        if use_gui:
            # The original PyQt6 setup is initiated here
            from PyQt6.QtWidgets import QApplication
            from setup import MainApp
            app = QApplication(sys.argv)
            main_app = MainApp()
            main_app.win.show()
            sys.exit(app.exec())
        else:
            # Fallback to TUI setup if no display is available
            run_tui_setup()
    
    # If setup is complete, run the server tray application
    if use_gui:
        from PyQt6.QtWidgets import QApplication
        from main_tray import ServerTrayApp
        app = QApplication(sys.argv)
        tray_app = ServerTrayApp()
        sys.exit(tray_app.run())
    else:
        # Add a non-GUI server-running loop here if needed
        print("Server running in headless mode. Use system commands to manage.")

if __name__ == "__main__":
    main()
