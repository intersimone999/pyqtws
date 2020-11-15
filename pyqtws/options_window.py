from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtCore import QSettings
from PyQt5.Qt import QShortcut, Qt, QObject
from PyQt5.QtGui import QIcon, QCloseEvent, QEnterEvent
from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEngineFullScreenRequest

from config import QTWSConfig
from web import QTWSWebView, QTWSWebPage
from plugins import QTWSPluginManager

import os

__home__ = os.path.dirname(os.path.realpath(__file__))


class QFileChooser(QWidget):
    def __init__(self, initial_value = None):
        super().__init__()
        
        if isinstance(initial_value, str):
            if self.check_file(initial_value):
                self.selected_file = initial_value
        elif isinstance(initial_value, list):
            for candidate in initial_value:
                if self.check_file(candidate):
                    self.selected_file = candidate
                    break
        
        self.text_box = QLineEdit()
        self.button   = QPushButton("Open")
        
        self.button.clicked.connect(lambda: self.__get_file())
        self.text_box.textChanged.connect(lambda text: self.__update(text))
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.text_box, 0, 0)
        self.layout.addWidget(self.button, 0, 1)
        
        self.setLayout(self.layout)
        self.show()
        
        if self.selected_file is not None:
            self.text_box.setText(self.selected_file)
        
    def check_file(self, file_name = False):
        if file_name is False:
            file_name = self.selected_file
            
        if file_name is None:
            return False
        
        if not os.path.isfile(file_name) or not os.access(file_name, os.X_OK):
            return False
        
        return True
    
    def setFile(self, value):
        self.text_box.setText(value)
    
    def __get_file(self):
        result = QFileDialog.getOpenFileName(self, 'Select program',  '/bin')
        if result is not None and result[0] is not None:
            self.text_box.setText(result[0])
    
    def __update(self, text):
        self.selected_file = text



class QTWSOptionsWindow(QWidget):
    SUGGESTED_FILES = ['/bin/chromium', '/bin/firefox', '/bin/vivaldi-stable', '/bin/falkon', '/bin/google-chrome-stable', '/bin/opera']
    
    def __init__(self, force = False):
        super().__init__()
        
        self.loaded_value = None
        self.app_settings = QSettings("silos", "Options", self)
        self.force = force
        self.__init_ui()

    def __init_ui(self):
        self.setWindowTitle("Silos Options")
        
        self.layout = QGridLayout()
        
        self.file_chooser = QFileChooser(self.SUGGESTED_FILES)
        
        self.layout.addWidget(QLabel("Browser", self), 0, 0)
        self.layout.addWidget(self.file_chooser, 0, 1)
        self.layout.addWidget(self.__build_ok_cancel_group(), 1, 1)
        self.layout.setContentsMargins(10, 5, 10, 5)
        
        self.__read_settings()
        self.setLayout(self.layout)
        
        self.show()
        
    def __build_ok_cancel_group(self):
        self.ok_button      = QPushButton("Ok")
        self.ok_button.clicked.connect(lambda: self.__on_ok())
        
        self.cancel_button  = QPushButton("Cancel")
        self.cancel_button.clicked.connect(lambda: self.__on_cancel())
        
        group = QGridLayout()
        group.addWidget(self.ok_button, 0, 0)
        group.addWidget(self.cancel_button, 0, 1)
        
        result = QWidget()
        result.setLayout(group)
        
        return result
    
    def closeEvent(self, event):
        if self.__on_cancel():
            event.accept()
        else:
            event.ignore()

    def __write_settings(self):
        self.app_settings.setValue("browser/defaultBrowser", self.file_chooser.selected_file)
    
    def __read_settings(self):
        value = self.app_settings.value("browser/defaultBrowser")
        if self.file_chooser.check_file(value):
            self.loaded_value = value
            self.file_chooser.setFile(value)

    def __on_ok(self):
        if not self.file_chooser.check_file():
            return self.__error("You have chosen a non-existing or a non-executable file.")
        
        self.__write_settings()
        self.loaded_value = self.file_chooser.selected_file
        QMessageBox().information(self, 'You are good to go!', 'You can now safely set silos as default web browser on your system: it will handle everything for you.', QMessageBox.Ok)
        self.close()
        return True
    
    def __on_cancel(self):
        if self.force and self.loaded_value is None:
            return self.__error("No previously selected broswer. You need to select a web broswer and press \"Ok\" to continue.")
        
        self.close()
        return True
    
    def __error(self, message):
        QMessageBox().critical(self, 'No valid broswer selected', message, QMessageBox.Ok)
        return False
