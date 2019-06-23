from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import QUrl
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
        QTWSPluginManager.instance().loadPlugins(self.config)
        self.__initUI(url)
        
    def __initUI(self, url=None):
        self.setWindowTitle(self.config.name)
        
        if url == None:
            url = self.config.home 
        
        self.web = QTWSWebView(self.config)
        self.web.load(QUrl(url))
        
        layout = QVBoxLayout()
        layout.addWidget(self.web)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.setLayout(layout)
        
        self.setWindowIcon(QIcon(self.config.icon))
        self.show()
        
    def closeEvent(self, event):
        if self.appChooser != None:
            self.appChooser.stopServing()
            
        super().closeEvent(event)
