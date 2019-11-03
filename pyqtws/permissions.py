from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenu
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineProfile

class QTWSPermissionManager:
    def __init__(self, web_page):
        self.web_page = web_page
        self.permissions_granted = []
        
        self.web_page.featurePermissionRequested.connect(self.__permission_check)
        
    def grant_permission(self, permission):
        if not permission in self.permissions_granted:
            self.permissions_granted.append(permission)
            
    def __permission_check(self, url, permission):
        if permission in self.permissions_granted:
            self.web_page.setFeaturePermission(url, permission, QWebEnginePage.PermissionGrantedByUser)
        else:
            self.web_page.setFeaturePermission(url, permission, QWebEnginePage.PermissionDeniedByUser)
