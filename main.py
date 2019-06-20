import sys

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon

from config import *
from web import QTWSWebView

class App(QWidget):
    def __init__(self, config_file):
        super().__init__()
        
        self.configuration = QTWSConfigParser(config_file)
        self.title = self.configuration.name
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        
        self.web = QTWSWebView()
        self.web.load(QUrl(self.configuration.home))
        
        layout = QVBoxLayout()
        layout.addWidget(self.web)
        layout.setContentsMargins(0,0,0,0)
        
        self.setLayout(layout)
        
        self.setWindowIcon( QIcon(self.configuration.icon) )
        self.show()
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App(sys.argv[1])
    sys.exit(app.exec_())
 
