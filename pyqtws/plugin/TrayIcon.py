from PyQt5.QtGui import QImage, QCloseEvent

from silo_window import QTWSMainWindow
from plugins import QTWSPlugin
from config import QTWSConfig

import pystray
from PIL import Image

import tempfile

class TrayIcon(QTWSPlugin):    
    def __init__(self, config: QTWSConfig):
        super().__init__("TrayIcon")
        self.window = None
        
        self.icon_path = tempfile.NamedTemporaryFile(suffix=".png").name
        
        tmp_image = QImage(config.icon)
        tmp_image.save(self.icon_path)
        
        self.menu = pystray.Menu(
            pystray.MenuItem(
                "Toggle visibility", 
                default=True, 
                action=lambda: self.__toggle_visibility()
            ),
            
            pystray.MenuItem(
                "Quit",
                action=lambda: self.__quit()
            )
        )
        
        self.tray_icon = pystray.Icon(
            config.name,
            Image.open(self.icon_path),
            menu=self.menu
        )
        
        self.tray_icon.visible = True
        self.tray_icon.run_detached()
                
    def close_event(self, window: QTWSMainWindow, event: QCloseEvent):
        self.__toggle_visibility()
        event.ignore()

    def window_setup(self, window: QTWSMainWindow):
        self.window = window
            
    def __toggle_visibility(self):
        self.window.setVisible(not self.window.isVisible())
    
    def __quit(self):
        self.tray_icon.stop()
        self.window.quit()


def instance(config: QTWSConfig, params: dict):
    return TrayIcon(config)
