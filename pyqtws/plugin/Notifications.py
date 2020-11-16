from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineProfile

from silo_window import QTWSMainWindow
from plugins import QTWSPlugin
from web import QTWSWebView
from config import QTWSConfig

import logging
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
            logging.error(f"Your system ({platform.system()}) is supported, but you miss the required python libraries.")
            Notifier.notifier = FallbackNotifier(app_name)
            
    def set_profile(profile):
        Notifier.profile = profile
        Notifier.profile.setNotificationPresenter(Notifier.notify)
            
    def notify(notification):
        Notifier.profile.setNotificationPresenter(Notifier.notify)
        Notifier.show_notification(notification)
        
    def show_notification(notification):
        notification.show()
        image_file = tempfile.NamedTemporaryFile(suffix=".png").name
        notification.icon().save(image_file)
        
        Notifier.notifier.show(notification, image_file)
        
        notification.close()
        os.remove(image_file)


class BasicNotifier:
    def show(self, notification, image_file):
        """
        Abstract notifier method call when a notification should be shown
        """
        pass
    

class LinuxNotifier(BasicNotifier):
    def __init__(self, app_name):
        try:
            import gi
            gi.require_version('Notify', '0.7')
            
            from gi.repository import Notify
            Notify.init(app_name)
            self.notifications_enabled = True
        except ImportError:
            logging.error("Notifications not enabled because the gi package is probably not available.")
            self.notifications_enabled = False
    
    def show(self, notification, image_file):
        if self.notifications_enabled:
            from gi.repository import Notify
            from gi.repository import GdkPixbuf
            
            image = GdkPixbuf.Pixbuf.new_from_file(image_file)
            
            notify = Notify.Notification.new(notification.title(), notification.message())
            notify.set_icon_from_pixbuf(image)
            notify.set_image_from_pixbuf(image)
            notify.set_urgency(1)
            
            notify.show()
    

class WindowsNotifier(BasicNotifier):
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


class FallbackNotifier(BasicNotifier):
    def __init__(self, app_name):
        logging.warning(f"{app_name} does not support notifications for your system. Using fallback notifier.")
    
    def show(self, notification, image_file):
        logging.warning(f"New notification! Title: {notification.title()}; Message: {notification.message()}")


def instance(config: QTWSConfig, params: dict):
    return Notifications(config)
