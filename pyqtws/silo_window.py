from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QSettings, QUrl, QObject, QTimer
from PyQt6.QtGui import QShortcut, QIcon, QCloseEvent, QEnterEvent
from PyQt6.QtWebEngineCore import QWebEngineFullScreenRequest

from config import QTWSConfig
from web import QTWSWebView, QTWSWebPage
from plugins import QTWSPluginManager


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
    def __init__(
        self, 
        app_id, 
        config_filename: str, 
        url: str = None, 
        profile: str = None
    ):
        super().__init__()
        
        self.__init_shortcuts()
        
        self.web = None
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

        self.stepping_url = url
        self.setGeometry(0, 28, 1000, 750)
        self.reset(app_id, config_filename, profile)
        
        self.__init_ui(url)
        self.__init_web_view()
        self.__read_settings()
        
        self.enter_event_handler = EnterEventHandler()
        self.setMouseTracking(True)
        self.installEventFilter(self.enter_event_handler)
        self.default_flags = self.windowFlags()
        self.show()
        
    def reset(
        self, 
        app_id, 
        config_filename: str, 
        profile: str = None
    ):
        self.config = QTWSConfig(config_filename, app_id)
        self.app_settings = QSettings(self.config.name, "Save State", self)
        
        self._profile_id = profile
        
        if self.web is not None:
            url = self.web.url().toString()
            if url != "":
                self.stepping_url = url
            self.layout.removeWidget(self.web)
            
        if not self.stepping_url or not self.config.in_scope(self.stepping_url):
            self.stepping_url = self.config.home
        
        if type(self.stepping_url) == QUrl:
            self.stepping_url = self.stepping_url.toString()
            
        self.stepping_url = self.stepping_url.replace('silo://', 'https://')

        self.web = QTWSWebView()
        self.layout.addWidget(self.web)
        self.loader_timer = QTimer(self)
        self.loader_timer.timeout.connect(self.go_to_stepping_url)
        self.loader_timer.start(1000)
        
        QTWSPluginManager.instance().each(
            lambda plugin: plugin.window_setup(self)
        )
        
    def go_to_stepping_url(self):
        self.web.initialize(self.config, self, self._profile_id)
        self.web.load(QUrl(self.stepping_url))
        self.loader_timer.stop()
        self.show()
        
    def closeEvent(self, event: QCloseEvent):
        self.__write_settings()
        
        QTWSPluginManager.instance().each(
            lambda plugin: plugin.close_event(self, event)
        )
        
    def quit(self):
        self.__action_quit()
    
    def profile_id(self):
        return self._profile_id
        
    def set_always_on_top(self, always_on_top: bool):
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, always_on_top)
        self.show()
    
    def set_maximizable(self, maximizable: bool):
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, maximizable)
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
            self.web.triggerPageAction(QTWSWebPage.WebAction.ExitFullScreen)
            if self.maximized:
                self.showNormal()
                self.showMaximized()
            else:
                self.showNormal()
    
    def set_mouse_enter_callback(self, callback):
        self.enter_event_handler.set_callback(callback)

    def __init_ui(self, url: str = None):
        self.setWindowTitle(f"{self.config.name}")

        self.setWindowIcon(QIcon(self.config.icon))
        QApplication.instance().setDesktopFileName("silo-" + self.config.app_id)
        self.show()

        self.maximized = self.isMaximized()
        
        if self.config.always_on_top:
            self.set_always_on_top(True)

    def __init_web_view(self):
        self.web.page().fullScreenRequested.connect(
            self.__full_screen_requested
        )

    def __full_screen_requested(self, request: QWebEngineFullScreenRequest):
        if request.toggleOn():
            self.maximized = self.isMaximized()
            self.showFullScreen()
        else:
            self.web.triggerPageAction(QTWSWebPage.WebAction.ExitFullScreen)
            if self.maximized:
                self.showNormal()
                self.showMaximized()
            else:
                self.showNormal()

        request.accept()

    def __write_settings(self):
        self.app_settings.setValue(
            "geometry/mainWindowGeometry", 
            self.saveGeometry()
        )

        if not self.config.save_session:
            return

        site = self.web.url().toString()
        self.app_settings.setValue("site", site)

    def __read_settings(self):
        if not self.config.save_session:
            return

        if self.config.save_session:
            geometry_data = self.app_settings.value(
                "geometry/mainWindowGeometry"
            )
            if geometry_data:
                self.restoreGeometry(geometry_data)

            site_data = self.app_settings.value("site")
            if site_data and site_data != "":
                self.web.setUrl(QUrl(site_data))

    def __init_shortcuts(self):
        self.__keyF11 = QShortcut(self)
        # self.__keyF11.setKey(Qt.Key.Key_F11)
        self.__keyF11.setKey("F11")
        self.__keyF11.activated.connect(self.__action_full_screen)

        self.__keyCtrlQ = QShortcut(self)
        # self.__keyCtrlQ.setKey(Qt.KeyboardModifier.ControlModifier + Qt.Key.Key_Q)
        self.__keyCtrlQ.setKey("Ctrl+Q")
        self.__keyCtrlQ.activated.connect(self.__action_quit)

        self.__keyCtrlH = QShortcut(self)
        # self.__keyCtrlH.setKey(Qt.KeyboardModifier.ControlModifier + Qt.Key.Key_H)
        self.__keyCtrlH.setKey("Ctrl+H")
        self.__keyCtrlH.activated.connect(self.__action_home)

        self.__keyCtrlR = QShortcut(self)
        # self.__keyCtrlR.setKey(Qt.KeyboardModifier.ControlModifier + Qt.Key.Key_R)
        self.__keyCtrlR.setKey("Ctrl+R")
        self.__keyCtrlR.activated.connect(self.__action_reload)

        self.__keyF5 = QShortcut(self)
        # self.__keyF5.setKey(Qt.Key.Key_F5)
        self.__keyF5.setKey("F5")
        self.__keyF5.activated.connect(self.__action_reload)

        self.__keyAltLeft = QShortcut(self)
        # self.__keyAltLeft.setKey(Qt.KeyboardModifier.AltModifier + Qt.Key.Key_Left)
        self.__keyAltLeft.setKey("Alt+Left")
        self.__keyAltLeft.activated.connect(self.__action_back)
        
        QTWSPluginManager.instance().each(
            lambda plugin: plugin.register_shortcuts(self)
        )

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
        QApplication.exit(0)

    def __action_reload(self):
        self.web.reload()
