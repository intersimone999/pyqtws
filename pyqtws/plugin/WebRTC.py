from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInfo
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtWebEngineCore import QWebEngineSettings

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
        self.web.grant_permission(QWebEnginePage.Feature.DesktopVideoCapture)
        self.web.grant_permission(QWebEnginePage.Feature.DesktopAudioVideoCapture)
        self.web.settings().setAttribute(
            QWebEngineSettings.WebAttribute.ScreenCaptureEnabled, 
            True
        )
    

def instance(config: QTWSConfig, params: dict):
    return WebRTC(config)
