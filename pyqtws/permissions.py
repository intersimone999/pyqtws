from PyQt6.QtWebEngineCore import QWebEnginePage


class QTWSPermissionManager:
    def __init__(self, web_page):
        self.web_page = web_page
        self.permissions_granted = []
        
        self.web_page.featurePermissionRequested.connect(
            self.__permission_check
        )
        
    def grant_permission(self, permission):
        if permission not in self.permissions_granted:
            self.permissions_granted.append(permission)
            
    def __permission_check(self, url, permission):
        if permission in self.permissions_granted:
            self.web_page.setFeaturePermission(
                url,
                permission,
                QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
            )
        else:
            self.web_page.setFeaturePermission(
                url,
                permission,
                QWebEnginePage.PermissionPolicy.PermissionDeniedByUser
            )
