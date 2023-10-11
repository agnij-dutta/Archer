import faulthandler
import threading

from flask import cli

from features.app import ArcherApp

faulthandler.enable()

threading.current_thread().name = "Archer"

cli.show_server_banner = lambda *x: None

if __name__ == "__main__":
    Archer_app = ArcherApp()

    Archer_app.start()
