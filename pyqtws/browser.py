import subprocess
import logging

from PyQt5.QtCore import QSettings


def open(url):
    silo_options = QSettings("silos", "Options")
    default_browser = silo_options.value("browser/defaultBrowser")
    if default_browser is None:
        app = QApplication(["silos"])
        ex = QTWSOptionsWindow(True)
        app.exec_()
    silo_options = QSettings("silos", "Options")
    default_browser = silo_options.value("browser/defaultBrowser")
    subprocess.call([default_browser, url])
    logging.info("Opened in the default external browser")
