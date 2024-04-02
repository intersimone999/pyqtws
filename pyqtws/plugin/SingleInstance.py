from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PyQt6.QtWidgets import QApplication

from dbus.service import Object

from silo_window import QTWSMainWindow
from plugins import QTWSPlugin
from web import QTWSWebView
from config import QTWSConfig

import logging
import os
import platform
import sys
import dbus
import dbus.mainloop.glib

class SingleInstance(QTWSPlugin):
    SERVICE_NAME = f"it.silos.Alive"
    
    def __init__(self, config: QTWSConfig):
        super().__init__("SingleInstance")
        self.config = config
        self.window = None
        self.object_name = f"/it/silos/Alive/{self.config.name}".replace(" ", "")
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    def app_setup(self, app: QApplication):
        bus = dbus.SessionBus()
        try:
            remote_object = bus.get_object(SingleInstance.SERVICE_NAME, self.object_name)

            reply = remote_object.Raise()
            sys.exit(0)
        except dbus.DBusException:
            pass
    
    def window_setup(self, window: QTWSMainWindow):
        self.window = window
        self.app_alive_interface = AppAliveInterface(self.object_name, self.window)


class AppAliveInterface(Object):
    def __init__(self, 
                 object_name: str,
                 window: QTWSMainWindow
                ):
        self.window = window
        self.bus = dbus.SessionBus()
        
        bus_name = dbus.service.BusName(
            SingleInstance.SERVICE_NAME,
            bus=self.bus
        )

        super().__init__(bus_name, object_name)

    @dbus.service.method(
        SingleInstance.SERVICE_NAME, 
        in_signature='', 
        out_signature=''
    )
    def Raise(self):
        self.window.setVisible(False)
        self.window.setVisible(True)

def instance(config: QTWSConfig, params: dict):
    return SingleInstance(config)
