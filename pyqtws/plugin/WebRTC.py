from PyQt6.QtWebEngineCore import QWebEnginePage

from plugins import QTWSPlugin
from web import QTWSWebView
from config import QTWSConfig


class WebRTC(QTWSPlugin):    
    def __init__(self, config: QTWSConfig):
        super().__init__("WebRTC")

    def web_engine_setup(self, web: QTWSWebView):
        self.web = web
        self.web.grant_permission(QWebEnginePage.Feature.MediaAudioVideoCapture)
        self.web.grant_permission(QWebEnginePage.Feature.MediaAudioCapture)
        self.web.grant_permission(QWebEnginePage.Feature.MediaVideoCapture)
        self.web.grant_permission(QWebEnginePage.Feature.DesktopAudioVideoCapture)
    

def instance(config: QTWSConfig, params: dict):
    return WebRTC(config)
