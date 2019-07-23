from PyQt5.QtCore import QUrl

from config import QTWSConfig
from plugins import QTWSPlugin


class GoogleAuthentication(QTWSPlugin):
    def __init__(self):
        super().__init__("GoogleAuthentication")

    def is_url_whitelisted(self, url: QUrl):
        url_string = url.toString()
        if url_string.startswith("https://accounts.google.com/signin") or \
                url_string.startswith("https://accounts.google.com/AddSession") or \
                url_string.startswith("https://accounts.google.com/ServiceLogin") or \
                url_string.startswith("https://accounts.google.com/o/oauth2"):
            return True

        return False


def instance(config: QTWSConfig, params: dict):
    return GoogleAuthentication()
