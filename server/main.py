import sys
import os
import sqlite3

#TODO: Write functions to connect to each app without the API (NoSSO)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from background.sqlite import create_connection, setup_database
from tui_setup import run_tui_setup

def is_setup_complete():
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

def noSSO():
    print("NoSSO access has been handed over to th")

def main():
    use_gui = os.environ.get("DISPLAY") is not None

    if not is_setup_complete():
        if use_gui:
            from PyQt6.QtWidgets import QApplication
            from setup import MainApp
            app = QApplication(sys.argv)
            main_app = MainApp()
            main_app.win.show()
            sys.exit(app.exec())
        else:
            run_tui_setup()
    if use_gui:
        from main_tray import ServerTrayApp
        app = ServerTrayApp()
        sys.exit(app.run())
    else:
        from main_tray import ServerTrayApp
        print("Headless")
        app = ServerTrayApp()
        sys.exit(app.run())

if __name__ == "__main__":
    main()
