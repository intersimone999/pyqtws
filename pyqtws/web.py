import webbrowser
import subprocess
import logging

from PyQt5.Qt import Qt
from PyQt5.QtCore import QPoint, QUrl
from PyQt5.QtWidgets import QApplication, QMessageBox, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView, QWebEngineSettings, QWebEngineProfile

from config import QTWSConfig
from plugins import QTWSPluginManager
from permissions import QTWSPermissionManager


class QTWSWebView(QWebEngineView):
    def __init__(self, config: QTWSConfig, window):
        super().__init__()
        self.config = config
        self.window = window
        self.webPage = QTWSWebPage(self.config)
        self.setPage(self.webPage)
        
        self.permission_manager = QTWSPermissionManager(self.webPage)
        
        QTWSPluginManager.instance().each(lambda plugin: plugin.web_engine_setup(self))

        if self.config.menu_disabled:
            self.setContextMenuPolicy(Qt.NoContextMenu)
        else:
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self.__show_menu)

        self.__create_actions()

        self.urlChanged.connect(self.__url_changed)

        self.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        self.settings().setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)

        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.downloadRequested.connect(lambda item: self.__download(item))
        self.profile.setCachePath(self.profile.cachePath() + "/" + self.config.name)
        self.profile.setPersistentStoragePath(self.profile.persistentStoragePath() + "/" + self.config.name)
        self.profile.setHttpCacheMaximumSize(self.config.cache_mb * 1024 * 1024)
        
        QTWSPluginManager.instance().each(lambda plugin: plugin.web_profile_setup(self.profile))
        
    def grant_permission(self, permission):
        self.permission_manager.grant_permission(permission)

    def __create_actions(self):
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
        for menu_item in self.config.menu:
            if menu_item.icon:
                action = QAction(QIcon.fromTheme(menu_item.icon), menu_item.title)
            else:
                action = QAction(menu_item.title)

            action.setData(menu_item.action)

            if menu_item.separator:
                self.__customActions.append("-")

            self.__customActions.append(action)

    def __show_menu(self, position: QPoint):
        self.menu = QMenu()

        if not self.page().history().canGoBack():
            self.__actionBack.setEnabled(False)
        self.menu.addAction(self.__actionBack)
        self.menu.addAction(self.__actionReload)
        self.menu.addAction(self.__actionHome)
        self.menu.addAction(self.__actionShare)

        if len(self.__customActions) > 0:
            self.menu.addSeparator()

        for action in self.__customActions:
            if action == '-':
                self.menu.addSeparator()
            else:
                self.menu.addAction(action)

        self.menu.addSeparator()

        for plugin in QTWSPluginManager.instance().plugins:
            plugin.add_menu_items(self.menu)
            self.menu.addSeparator()

        self.menu.addAction(self.__actionQuit)

        # Handles all the custom actions using the URL stored in the action's data field
        self.menu.triggered.connect(self.__menu_click)
        self.menu.popup(self.mapToGlobal(position))
        
    def __download(self, item):
        url = item.url().toString()
        webbrowser.open(url)
        item.cancel()

    def __share(self):
        QApplication.instance().clipboard().setText(self.url().toString())
        QMessageBox().information(self, 'Shared', 'Copied to the clipboard', QMessageBox.Ok)

    def __quit(self):
        self.window.quit()

    def __menu_click(self, action: QAction):
        if action.data():
            self.setUrl(action.data())

    def __url_changed(self, status):
        QTWSPluginManager.instance().each(lambda plugin: plugin.on_page_loaded(self.url()))


class QTWSWebPage(QWebEnginePage):
    def __init__(self, config: QTWSConfig):
        super().__init__()
        self.config = config

    def createWindow(self, t):
        fake_page = QWebEnginePage(self)
        fake_page.urlChanged.connect(lambda url: self.__create_window_request(fake_page, url))

        return fake_page

    def acceptNavigationRequest(self, url: QUrl, request_type, is_main_frame: bool):
        if request_type != QWebEnginePage.NavigationTypeLinkClicked:
            return True

        if not is_main_frame:
            return True

        if not self.__check_in_scope(url):
            self.__open_outside_url(url)
            return False
        else:
            return True

    def __create_window_request(self, fake_page: QWebEnginePage, url: QUrl):
        if not self.__check_in_scope(url):
            if url.scheme != 'about' and url.scheme != "":
                self.__open_outside_url(url)
                return False
        else:
            self.setUrl(url)
            return False
        
    def __open_outside_url(self, url):
        silo_url = url.toString().replace("https://", "silo://").replace("http://", "silo://")
        logging.info("Going outside because of {}: redirecting to {}".format(url.toString(), silo_url))
        subprocess.Popen(['silo', silo_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    def __check__blacklisted(self, url: QUrl):
        for plugin in QTWSPluginManager.instance().plugins:
            if plugin.is_url_blacklisted(url):
                return True

        return False

    def __check_whitelisted(self, url: QUrl):
        for plugin in QTWSPluginManager.instance().plugins:
            if plugin.is_url_whitelisted(url):
                return True

        return False

    def __check_in_scope(self, url: QUrl):
        if self.__check_whitelisted(url):
            return True

        url_out_of_scope = not self.config.in_scope(url)
        plugin_blacklist = self.__check__blacklisted(url)
        if url_out_of_scope or plugin_blacklist:
            return False
        else:
            return True
