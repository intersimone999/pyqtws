from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import QUrl, QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView

from config import *
from web import QTWSWebView, QTWSWebPage
from plugins import QTWSPluginManager

class QTWSMainWindow(QWidget):
    def __init__(self, configFilename, url, appChooser=None):
        super().__init__()
        
        self.config = QTWSConfig(configFilename)
        self.appChooser = appChooser
        self.appSettings = QSettings(self.config.name, "Save State", self);
        
        QTWSPluginManager.instance().loadPlugins(self.config)
        self.__initUI(url)
        self.__readSettings()
        
    def closeEvent(self, event):
        self.__writeSettings()
        if self.appChooser:
            self.appChooser.stopServing()
            
        super().closeEvent(event)
        
    def __initUI(self, url=None):
        self.setWindowTitle(self.config.name)
        
        if not url:
            url = self.config.home 
        
        self.web = QTWSWebView(self.config)
        self.web.load(QUrl(url))
        
        layout = QVBoxLayout()
        layout.addWidget(self.web)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.setLayout(layout)
        
        self.setWindowIcon(QIcon(self.config.icon))
        self.show()
    
    def __writeSettings(self):
        self.appSettings.setValue("geometry/mainWindowGeometry", self.saveGeometry())

        if not self.config.saveSession:
            return

        self.appSettings.setValue("state/mainWindowState", self.saveState())

        site = self.web.url().toString()
        self.appSettings.setValue("site", site)
        
    def __readSettings(self):
        if not self.config.saveSession or self.appSettings.value("state/mainWindowState"):
            return
        
        if self.config.saveSession:
            stateData = self.appSettings.value("state/mainWindowState").toByteArray()
            self.restoreState(stateData)

        geometryData = self.appSettings.value("geometry/mainWindowGeometry").toByteArray()
        self.restoreGeometry(geometryData)

        if self.appSettings.value("site").toString() != "":
            self.web.setUrl(QUrl(self.appSettings.value("site").toString()))
