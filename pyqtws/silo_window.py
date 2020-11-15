from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import QSettings, QUrl
from PyQt5.Qt import QShortcut, Qt, QObject
from PyQt5.QtGui import QIcon, QCloseEvent, QEnterEvent
from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEngineFullScreenRequest

from config import QTWSConfig
from web import QTWSWebView, QTWSWebPage
from plugins import QTWSPluginManager

import os

__home__ = os.path.dirname(os.path.realpath(__file__))


class EnterEventHandler(QObject):
    def __init__(self):
        super().__init__()
        self.set_callback(None)
        
    def set_callback(self, callback):
        self.callback = callback
        
    def eventFilter(self, obj, event):
        if type(event) is QEnterEvent:
            if self.callback is not None:
                self.callback(event)
            return True
        else:
            return False


class QTWSMainWindow(QWidget):
    def __init__(self, app_id, config_filename: str, url: str = None):
        super().__init__()

        self.config = QTWSConfig(config_filename, app_id)
        self.app_settings = QSettings(self.config.name, "Save State", self)

        QTWSPluginManager.instance().load_plugins(self.config)
        self.__init_ui(url)
        self.__init_web_view()
        self.__read_settings()
        self.__init_shortcuts()
        
        self.enter_event_handler = EnterEventHandler()
        self.setMouseTracking(True)
        self.installEventFilter(self.enter_event_handler)
        self.default_flags = self.windowFlags()

        QTWSPluginManager.instance().each(lambda plugin: plugin.window_setup(self))

    def closeEvent(self, event: QCloseEvent):
        self.__write_settings()
        
        QTWSPluginManager.instance().each(lambda plugin: plugin.close_event(self, event))
        
    def quit(self):
        self.__action_quit()
        
    def set_always_on_top(self, always_on_top: bool):
        self.setWindowFlag(Qt.WindowStaysOnTopHint, always_on_top)
        self.show()
    
    def set_maximizable(self, maximizable: bool):
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, maximizable)
        self.show()
        
    def reset_flags(self):
        self.setWindowFlags(self.default_flags)
        self.show()
        
    def activate_fullscreen(self):
        if not self.isFullScreen():
            self.maximized = self.isMaximized()
            self.showFullScreen()
            
    def deactivate_fullscreen(self):
        if self.isFullScreen():
            self.web.triggerPageAction(QTWSWebPage.ExitFullScreen)
            if self.maximized:
                self.showNormal()
                self.showMaximized()
            else:
                self.showNormal()
    
    def set_mouse_enter_callback(self, callback):
        self.enter_event_handler.set_callback(callback)

    def __init_ui(self, url: str = None):
        self.setWindowTitle(self.config.name)

        if not url or not self.config.in_scope(url):
            url = self.config.home
        
        if type(url) == QUrl:
            url = url.toString()
            
        url = url.replace('silo://', 'https://')

        self.web = QTWSWebView(self.config, self)
        self.web.load(QUrl(url))

        layout = QVBoxLayout()
        layout.addWidget(self.web)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        self.setWindowIcon(QIcon(os.path.join(__home__, self.config.icon)))
        self.show()

        self.maximized = self.isMaximized()

    def __init_web_view(self):
        profile = QWebEngineProfile.defaultProfile()

        profile.setCachePath(profile.cachePath() + "/" + self.config.name)
        profile.setPersistentStoragePath(profile.persistentStoragePath() + "/" + self.config.name)
        profile.setHttpCacheMaximumSize(self.config.cache_mb * 1024 * 1024)

        self.web.page().fullScreenRequested.connect(self.__full_screen_requested)

        if self.config.always_on_top:
            self.set_always_on_top(True)

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
        
        QTWSPluginManager.instance().each(lambda plugin: plugin.register_shortcuts(self))

    def __action_back(self):
        self.web.back()

    def __action_full_screen(self):
        if not self.isFullScreen():
            self.activate_fullscreen()
        else:
            self.deactivate_fullscreen()

    def __action_home(self):
        self.web.setUrl(self.config.home)

    def __action_quit(self):
        self.__write_settings()
        QApplication.quit()

    def __action_reload(self):
        self.web.reload()
