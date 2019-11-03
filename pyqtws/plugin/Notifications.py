from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineProfile

from mainwindow import QTWSMainWindow
from plugins import QTWSPlugin
from web import QTWSWebView
from config import QTWSConfig

import tempfile
import os

import platform


class Notifications(QTWSPlugin):    
    def __init__(self, config: QTWSConfig):
        super().__init__("Notifications")
        
        Notifier.init(config.name)

    def window_setup(self, window: QTWSMainWindow):
        self.window = window

    def web_engine_setup(self, web: QTWSWebView):
        self.web = web
        self.web.grant_permission(QWebEnginePage.Notifications)
    
    def web_profile_setup(self, profile: QWebEngineProfile):
        Notifier.set_profile(profile)

class Notifier:
    notifier = None
    profile = None
    
    def init(app_name):
        try:
            if 'linux' in platform.system().lower():
                Notifier.notifier = LinuxNotifier(app_name)
            elif 'windows' in platform.system().lower():
                Notifier.notifier = WindowsNotifier(app_name)
            else:
                Notifier.notifier = FallbackNotifier(app_name)
                
        except ImportError:
            print("Your system ({}) is supported, but you miss the required python libraries.".format(platform.system()))
            Notifier.notifier = FallbackNotifier(app_name)
            
    def set_profile(profile):
        Notifier.profile = profile
        Notifier.profile.setNotificationPresenter(Notifier.notify)
            
    def notify(notification):
        Notifier.profile.setNotificationPresenter(Notifier.notify)
        Notifier.show(notification)
        
    def show(notification):
        notification.show()
        image_file = tempfile.NamedTemporaryFile(suffix=".png").name
        notification.icon().save(image_file)
        
        Notifier.notifier.show(notification, image_file)
        
        notification.close()
        os.remove(image_file)
                
        
class LinuxNotifier:
    def __init__(self, app_name):
        from gi.repository import Notify
        Notify.init(app_name)
    
    def show(self, notification, image_file):
        from gi.repository import Notify
        from gi.repository import GdkPixbuf
        
        image = GdkPixbuf.Pixbuf.new_from_file(image_file)

        notify = Notify.Notification.new(notification.title(), notification.message())
        notify.set_icon_from_pixbuf(image)
        notify.set_image_from_pixbuf(image)
        notify.set_urgency(1)
        
        notify.show()
    
class WindowsNotifier:
    def __init__(self, app_name):
        import win10toast
    
    def show(self, notification, image_file):
        import win10toast
        win10toast.ToastNotifier().show_toast(
                threaded=True,
                title=notification.title(),
                msg=notification.message(),
                duration=5,
                icon_path=None
        )
    
class FallbackNotifier:
    def __init__(self, app_name):
        print("{} does not support notifications for your system. Using fallback notifier.".format(app_name))
    
    def show(self, notification, image_file):
        print("------------------------------")
        print("New notification!\n\tTitle: {}\n\tMessage: {}".format(notification.title(), notification.message()))
        print("------------------------------")

def instance(config: QTWSConfig, params: dict):
    return Notifications(config)
