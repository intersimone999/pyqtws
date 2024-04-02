from PyQt6.QtGui import QIcon, QShortcut, QAction
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMenu, QApplication, QMessageBox

from silo_window import QTWSMainWindow
from plugins import QTWSPlugin
from config import QTWSConfig


class FloatingWindow(QTWSPlugin):
    def __init__(self, config):
        super().__init__("FloatingWindow")
        self.window = None
        self.config = config
        self.floating_toggle = None
        self.is_window_floating = False
        self.message_box_shown = False
        
    def window_setup(self, window: QTWSMainWindow):
        self.window = window
        
    def register_shortcuts(self, window):
        self.__keyCtrlF = QShortcut(window)
        self.__keyCtrlF.setKey("CTRL+F")
        self.__keyCtrlF.activated.connect(lambda: self.__activate_floating())

    def add_menu_items(self, menu: QMenu):
        self.floating_toggle = None
        self.floating_toggle = QAction(
            QIcon.fromTheme("file-zoom-out"),
            "Enable floating window"
        )
        
        self.floating_toggle.triggered.connect(
            lambda: self.__activate_floating()
            )
        menu.addAction(self.floating_toggle)
        
    def close_event(self, window: QTWSMainWindow, event):
        if self.is_window_floating:
            self.__deactivate_floating()
            event.ignore()
    
    def __activate_floating(self):
        box = QMessageBox()
        box.setWindowTitle("Floating mode deprecated")
        box.setText("The floating mode is now deprecated. Please ignore this plugin.")
        box.setIcon(QMessageBox.Icon.Information)
        box.exec()
        return
    
        if self.is_window_floating:
            return
        
        self.screen = QApplication.instance().primaryScreen().geometry()
        
        self.previous_x = self.window.x()
        self.previous_y = self.window.y()
        
        self.previous_width = self.window.width()
        self.previous_height = self.window.height()
        self.previous_max_width = self.window.maximumWidth()
        self.previous_max_height = self.window.maximumHeight()
        
        self.previously_maximized = self.window.isMaximized()
        self.previously_fullscreen = self.window.isFullScreen()
                
        self.window.set_always_on_top(True)
        self.window.setMaximumWidth(int(self.screen.width() / 2))
        self.window.setMaximumHeight(int(self.screen.height() / 2))
        
        self.window.resize(int(self.screen.width() / 3), int(self.screen.height() / 3))
        self.window.set_mouse_enter_callback(lambda e: self.__on_focus(e))
        self.window.set_maximizable(False)
        self.__on_focus(None)
        self.is_window_floating = True
        
        if not self.message_box_shown:
            box = QMessageBox()
            box.setWindowTitle("Floating mode activated")
            box.setText("Just close the window to disable the floating mode.")
            box.setIcon(QMessageBox.Icon.Information)
            box.exec()
            self.message_box_shown = True
    
    def __deactivate_floating(self):    
        self.window.setMaximumWidth(self.previous_max_width)
        self.window.setMaximumHeight(self.previous_max_height)
        
        self.window.resize(self.previous_width, self.previous_height)
        self.window.move(self.previous_x, self.previous_y)
        
        if not self.config.always_on_top:
            self.window.set_always_on_top(False)
            
        self.window.set_maximizable(True)
        self.window.set_mouse_enter_callback(None)
        self.is_window_floating = False
        
        self.window.showNormal()
        if self.previously_maximized:
            self.window.showMaximized()
            
        if self.previously_fullscreen:
            self.window.activate_fullscreen()
        
    def __on_focus(self, event):
        self.screen = QApplication.instance().primaryScreen().geometry()
        
        y = self.screen.height() - self.window.height()
        if event is not None and event.globalPosition().x() < self.window.width():
            x = self.screen.width() - self.window.width()
            self.window.move(x, y)
        else:
            self.window.move(0, y)


def instance(config: QTWSConfig, params: dict):
    return FloatingWindow(config)
