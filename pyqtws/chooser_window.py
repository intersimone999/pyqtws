from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton, QMessageBox
from PyQt6.QtGui import QIcon

from config import QTWSConfig

import os
import sys
import glob
import webbrowser


class QAppWidget(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.layout = QGridLayout()

        self.can_open = True

        self.icon = QIcon(self.app.icon)
        self.button = QPushButton(self.app.name)
        self.button.setIcon(self.icon)
        self.button.setStyleSheet(
            "QPushButton { text-align: left; padding: 8px; }"
        )
        self.clicked = self.button.clicked
        self.clicked.connect(lambda: self.open_app())
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)
        self.show()

    def open_app(self):
        if not self.can_open:
            return

        self.can_open = False
        webbrowser.open(f"silo://start#{self.app.app_id}")
        sys.exit(0)


class QTWSChooserWindow(QWidget):
    ELEMENTS_PER_ROW = 3

    def __init__(self, apps_folder):
        super().__init__()
        self.__load_app_configs(apps_folder)
        if len(self.apps) > 0:
            self.__init_ui()
        else:
            QMessageBox().warning(
                self, 
                'No apps available', 
                'No apps installed. Please install at least an app.', 
                QMessageBox.StandardButton.Ok
            )
            sys.exit(0)

    def __load_app_configs(self, folder):
        self.apps = []
        for config_path in glob.glob(os.path.join(folder, "*.qtws")):
            app_id = os.path.basename(config_path).replace('.qtws', '')
            self.apps.append(QTWSConfig(config_path, app_id))

    def __init_ui(self):
        self.setWindowTitle("Silos")

        self.layout = QGridLayout()

        self.app_widgets = {}
        index = 0
        for app in self.apps:
            row = int(index / self.ELEMENTS_PER_ROW)
            col = index % self.ELEMENTS_PER_ROW

            widget = QAppWidget(app)
            self.app_widgets[app.app_id] = widget
            widget.clicked.connect(lambda: self.close())
            self.layout.addWidget(widget, row, col)
            index += 1

        self.layout.setContentsMargins(10, 5, 10, 5)
        self.setLayout(self.layout)
        self.show()
