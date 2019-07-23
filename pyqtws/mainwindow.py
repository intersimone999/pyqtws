from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import QSettings
from PyQt5.Qt import QShortcut, Qt
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEngineFullScreenRequest

from appchooser import AppChooser
from config import *
from web import QTWSWebView, QTWSWebPage
from plugins import QTWSPluginManager

import os

__home__ = os.path.dirname(os.path.realpath(__file__))


class QTWSMainWindow(QWidget):
    def __init__(self, app_id, config_filename: str, url: str, app_chooser: AppChooser = None):
        super().__init__()

        self.config = QTWSConfig(config_filename, app_id)
        self.app_chooser = app_chooser
        self.app_settings = QSettings(self.config.name, "Save State", self)

        QTWSPluginManager.instance().load_plugins(self.config)
        self.__init_ui(url)
        self.__init_web_view()
        self.__read_settings()
        self.__init_shortcuts()

        QTWSPluginManager.instance().each(lambda plugin: plugin.window_setup(self))

    def closeEvent(self, event: QCloseEvent):
        self.__write_settings()
        if self.app_chooser:
            self.app_chooser.stop_serving()

        super().closeEvent(event)

    def __init_ui(self, url: str = None):
        self.setWindowTitle(self.config.name)

        if not url:
            url = self.config.home

        self.web = QTWSWebView(self.config)
        self.web.load(QUrl(url))

        layout = QVBoxLayout()
        layout.addWidget(self.web)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        self.setWindowIcon(QIcon(os.path.join(__home__, self.config.icon)))
        self.show()

    def __init_web_view(self):
        profile = QWebEngineProfile.defaultProfile()

        profile.setCachePath(profile.cachePath() + "/" + self.config.name)
        profile.setPersistentStoragePath(profile.persistentStoragePath() + "/" + self.config.name)
        profile.setHttpCacheMaximumSize(self.config.cache_mb * 1024 * 1024)

        self.web.page().fullScreenRequested.connect(self.__full_screen_requested)

        if self.config.always_on_top:
            self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def __full_screen_requested(self, request: QWebEngineFullScreenRequest):
        if request.toggleOn():
            self.maximized = self.isMaximized()
            self.showFullScreen()
        else:
            self.web.triggerPageAction(QTWSWebPage.ExitFullScreen)
            if self.maximized:
                self.showNormal()
                self.showMaximized()
            else:
                self.showNormal()

        request.accept()

    def __write_settings(self):
        self.app_settings.setValue("geometry/mainWindowGeometry", self.saveGeometry())

        if not self.config.save_session:
            return

        site = self.web.url().toString()
        self.app_settings.setValue("site", site)

    def __read_settings(self):
        if not self.config.save_session or self.app_settings.value("state/mainWindowState"):
            return

        if self.config.save_session:
            geometry_data = self.app_settings.value("geometry/mainWindowGeometry")
            if geometry_data:
                self.restoreGeometry(geometry_data)

            site_data = self.app_settings.value("site")
            if site_data and site_data != "":
                self.web.setUrl(QUrl(site_data))

    def __init_shortcuts(self):
        self.__keyF11 = QShortcut(self)
        self.__keyF11.setKey(Qt.Key_F11)
        self.__keyF11.activated.connect(self.__action_full_screen)

        self.__keyCtrlQ = QShortcut(self)
        self.__keyCtrlQ.setKey(Qt.CTRL + Qt.Key_Q)
        self.__keyCtrlQ.activated.connect(self.__action_quit)

        self.__keyCtrlH = QShortcut(self)
        self.__keyCtrlH.setKey(Qt.CTRL + Qt.Key_H)
        self.__keyCtrlH.activated.connect(self.__action_home)

        self.__keyCtrlR = QShortcut(self)
        self.__keyCtrlR.setKey(Qt.CTRL + Qt.Key_R)
        self.__keyCtrlR.activated.connect(self.__action_reload)

        self.__keyF5 = QShortcut(self)
        self.__keyF5.setKey(Qt.Key_F5)
        self.__keyF5.activated.connect(self.__action_reload)

        self.__keyAltLeft = QShortcut(self)
        self.__keyAltLeft.setKey(Qt.ALT + Qt.Key_Left)
        self.__keyAltLeft.activated.connect(self.__action_back)

    def __action_back(self):
        self.web.back()

    def __action_full_screen(self):
        if not self.isFullScreen():
            self.maximized = self.isMaximized()
            self.showFullScreen()
        else:
            self.web.triggerPageAction(QTWSWebPage.ExitFullScreen)
            if self.maximized:
                self.showNormal()
                self.showMaximized()
            else:
                self.showNormal()

    def __action_home(self):
        self.web.setUrl(self.config.home)

    def __action_quit(self):
        self.__write_settings()
        QApplication.quit()

    def __action_reload(self):
        self.web.reload()
