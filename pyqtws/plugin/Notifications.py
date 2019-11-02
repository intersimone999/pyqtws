from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenu
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineProfile

from mainwindow import QTWSMainWindow
from plugins import QTWSPlugin
from web import QTWSWebView
from config import QTWSConfig

import main

import random
import time
import dbus
import dbus.mainloop.glib
import tempfile
import os

from gi.repository import Notify, GdkPixbuf


class Notifications(QTWSPlugin):
    app_icon    = None
    can_notify  = False
    profile     = None
    
    def __init__(self, config: QTWSConfig):
        super().__init__("Notifications")
        self.web = None
        self.window = None
        self.config = config
        self.profile = None
        
        Notifier.init(self.config.name, True)
        #Notifications.can_notify = os.system("notify-send --help &> /dev/null") == 0

    def window_setup(self, window: QTWSMainWindow):
        self.window = window

    def web_engine_setup(self, web: QTWSWebView):
        self.web = web
        self.web.page().featurePermissionRequested.connect(lambda url, feature: self.web.page().setFeaturePermission(url, feature, QWebEnginePage.PermissionGrantedByUser))

    def on_page_loaded(self, url: QUrl):
        pass

    def add_menu_items(self, menu: QMenu):
        pass
    
    def web_profile_setup(self, profile: QWebEngineProfile):
        Notifications.profile = profile
        profile.setNotificationPresenter(Notifications.notify)
        
    def notify(notification):
        Notifications.profile.setNotificationPresenter(Notifications.notify)
        Notifier.show(notification)

class Notifier:
    can_notify = False
    
    def init(app_name, can_notify):
        Notify.init(app_name)
        Notifier.can_notify = can_notify
        
    def show(notification):
        notification.show()
        
        image_file = tempfile.NamedTemporaryFile(suffix=".png").name
        notification.icon().save(image_file)

        title    = notification.title()
        body     = notification.message()
        
        notify = Notify.Notification.new(title, body)
        
        image = GdkPixbuf.Pixbuf.new_from_file(image_file)

        notify.set_icon_from_pixbuf(image)
        notify.set_image_from_pixbuf(image)
        
        notify.show()       
        notification.close()
        
        os.remove(image_file)

def instance(config: QTWSConfig, params: dict):
    return Notifications(config)
