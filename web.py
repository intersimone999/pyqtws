from threading import Thread
import webbrowser

from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QApplication, QMessageBox, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWebEngineWidgets import QWebEngineView

from plugins import QTWSPluginManager

class QTWSWebView(QWebEngineView):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.webPage = QTWSWebPage(self.config)
        self.setPage(self.webPage)
        QTWSPluginManager.instance().forEach(lambda plugin: plugin.webEngineSetup(self))
        
        if self.config.menuDisabled:
            self.setContextMenuPolicy(Qt.NoContextMenu);
        else:
            self.setContextMenuPolicy(Qt.CustomContextMenu);
            self.customContextMenuRequested.connect(self.__showMenu)
            
        self.__createActions()
            
    def __createActions(self):
        self.__actionBack = QAction(QIcon.fromTheme("back"), "Back")
        self.__actionBack.triggered.connect(lambda: self.back())
        
        self.__actionReload = QAction(QIcon.fromTheme("reload"), "Reload")
        self.__actionReload.triggered.connect(lambda: self.reload())
        
        self.__actionHome = QAction(QIcon.fromTheme("go-home"), "Home")
        self.__actionHome.triggered.connect(lambda: self.setUrl(self.config.home))
        
        self.__actionShare = QAction(QIcon.fromTheme("emblem-shared"), "Share")
        self.__actionShare.triggered.connect(self.__share)
        
        self.__actionQuit = QAction(QIcon.fromTheme("application-exit"), "Quit")
        self.__actionQuit.triggered.connect(self.__quit)
        
        self.__customActions = list()
        for menuItem in self.config.menu:
            action = None
            if menuItem.icon != None:
                action = QAction(QIcon.fromTheme(menuItem.icon), menuItem.title)
            else:
                action = QAction(menuItem.title)
            
            action.setData(menuItem.action)
            
            if menuItem.separator:
                self.__customActions.append("-")
                
            self.__customActions.append(action)
                
    def __showMenu(self, position):
        self.menu = QMenu()
        
        
        if not self.page().history().canGoBack():
            self.__actionBack.setEnabled(False)
        self.menu.addAction(self.__actionBack)
        self.menu.addAction(self.__actionReload)
        self.menu.addAction(self.__actionHome)
        self.menu.addAction(self.__actionShare)
        
        if (len(self.__customActions) > 0):
            self.menu.addSeparator()
        
        for action in self.__customActions:
            if action == '-':
                self.menu.addSeparator()
            else:
                self.menu.addAction(action)
            
        self.menu.addSeparator()
        
        for plugin in QTWSPluginManager.instance().plugins:
            plugin.addMenuItems(self.menu)
            self.menu.addSeparator()
        
        self.menu.addAction(self.__actionQuit)
        
        # Handles all the custom actions using the URL stored in the action's data field
        self.menu.triggered.connect(self.__menuClick)
        self.menu.popup(self.mapToGlobal(position))
            
    def __share(self):
        QApplication.instance().clipboard().setText(self.url().toString())
        QMessageBox.information(self, 'Shared', 'Copied to the clipboard', QMessageBox.Ok)
        
    def __quit(self):
        # TODO write settings
        QApplication.quit()
        
    def __menuClick(self, action):
        if action.data() != None:
            self.setUrl(action.data())
        
class QTWSWebPage(QWebEnginePage):
    def __init__(self, config):
        super().__init__()
        self.config = config
        
    def createWindow(self, t):
        fakePage = QWebEnginePage(self);
        fakePage.urlChanged.connect(lambda url: self.__createWindowRequest(fakePage, url))

        return fakePage
    
    def acceptNavigationRequest(self, url, requestType, isMainFrame):
        if requestType != QWebEnginePage.NavigationTypeLinkClicked:
            return True
        
        if not isMainFrame:
            return True
        
        urlOutOfScope   = not self.config.isInScope(url)
        pluginBlocksUrl = self.__checkIfAnyPluginBlocks(url)
        if urlOutOfScope or pluginBlocksUrl:
            webbrowser.open(url.toString())
            return False
        else:
            return True
    
    def __checkIfAnyPluginBlocks(self, url):
        for plugin in QTWSPluginManager.instance().plugins:
            if plugin.isURLBlocked(url):
                return True
        
        return False
    
    def __createWindowRequest(self, fakePage, url):
        if not self.config.isInScope(url):
            if url.scheme != 'about' and url.scheme != "":
                webbrowser.open(url.toString())
        else:
            self.setUrl(url)
