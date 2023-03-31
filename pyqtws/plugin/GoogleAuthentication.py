from PyQt5.QtCore import QUrl

from config import QTWSConfig
from plugins import QTWSPlugin


class GoogleAuthentication(QTWSPlugin):
    def __init__(self):
        super().__init__("GoogleAuthentication")

    def is_url_whitelisted(self, qurl: QUrl):
        url = qurl.toString()
        if url.startswith("https://accounts.google.com/signin") or \
                url.startswith("https://accounts.google.com/AddSession") or \
                url.startswith("https://accounts.google.com/ServiceLogin") or \
                url.startswith("https://accounts.google.com/o/oauth2") or \
                url.startswith("https://accounts.google.com/v3/signin"):
            return True

        return False


def instance(config: QTWSConfig, params: dict):
    return GoogleAuthentication()
