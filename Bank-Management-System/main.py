"""Bank Management System entry point.

Default: graphical interface.
Use `python main.py --cli` to launch the original command-line interface.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager


def main():
    if "--cli" in sys.argv:
        from cli.main_menu import MainMenu
        from utils.logger import log_event, get_logger
        get_logger()
        db = DatabaseManager()
        db.seed_demo_data()
        log_event("SYSTEM_STARTUP", "Bank Management System CLI initialized.")
        MainMenu(db).run()
    else:
        from gui import run_gui
        run_gui()


if __name__ == "__main__":
    main()
