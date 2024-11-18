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
#         
    def add_menu_items(self, menu: QMenu):
        self.floating_toggle = None
        self.floating_toggle = QAction(
            QIcon.fromTheme("file-zoom-out"),
            "Enable floating window (deprecated)"
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
