import sys

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView

from config import *
from web import QTWSWebView, QTWSWebPage
from plugins import QTWSPluginManager

class QTWSMainWindow(QWidget):
    def __init__(self, configFilename):
        super().__init__()
        
        self.config = QTWSConfig(configFilename)
        QTWSPluginManager.instance().loadPlugins(self.config)
        self.__initUI()
        
    def __initUI(self):
        self.setWindowTitle(self.config.name)
        
        self.web = QTWSWebView(self.config)
        self.web.load(QUrl(self.config.home))
        
        layout = QVBoxLayout()
        layout.addWidget(self.web)
        layout.setContentsMargins(0,0,0,0)
        
        self.setLayout(layout)
        
        self.setWindowIcon(QIcon(self.config.icon))
        self.show()
 
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = QTWSMainWindow(sys.argv[1])
    sys.exit(app.exec_())
 


