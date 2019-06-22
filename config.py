import json
import re

from PyQt5.QtCore import QUrl

class QTWSConfig:
    def __init__(self, configFilename):
        with open(configFilename) as f:
            self.completeJson = json.load(f)
        self.__loadData()

    def __loadData(self):
        try:
            self.name = self.completeJson['name']
            if type(self.name) != str:
                raise QTWSConfigException("The parameter name should be a string parameter")
            if "/" in self.name or "//" in self.name:
                raise QTWSConfigException("Illegal name " + self.name + ": it cannot contain slashes or backslashes.")
        except KeyError:
            raise QTWSConfigException("Cannot find the name in the configuration file")
        
        try:
            self.scope = self.completeJson['scope']
            if type(self.scope) != list:
                raise QTWSConfigException("The scope should be an array")
        except KeyError:
            raise QTWSConfigException("Cannot find the scope in the configuration file")
        
        try:
            self.home = self.completeJson['home']
            if type(self.home) != str:
                raise QTWSConfigException("The parameter home should be a string parameter")
            
            self.home = QUrl(self.home)
        except KeyError:
            raise QTWSConfigException("Cannot find the home in the configuration file")
        
        try:
            self.icon = self.completeJson['icon']
            if type(self.icon) != str:
                raise QTWSConfigException("The parameter icon should be a string parameter")
        except KeyError:
            raise QTWSConfigException("Cannot find the icon in the configuration file")
        
        try:
            self.cacheMB = self.completeJson['cacheMB']
            if type(self.cacheMB) != int:
                raise QTWSConfigException("The parameter cacheMB should be an integer parameter")
        except KeyError:
            self.cacheMB = 50
        
        try:
            self.saveSession = self.completeJson['saveSession']
            if type(self.saveSession) != bool:
                raise QTWSConfigException("The parameter saveSession should be a boolean parameter")
        except KeyError:
            self.saveSession = False
            
        try:
            self.menuDisabled = self.completeJson['menuDisabled']
            if type(self.menuDisabled) != bool:
                raise QTWSConfigException("The parameter menuDisabled should be a boolean parameter")
        except KeyError:
            self.menuDisabled = False
            
        try:
            self.alwaysOnTop = self.completeJson['alwaysOnTop']
            if type(self.alwaysOnTop) != bool:
                raise QTWSConfigException("The parameter alwaysOnTop should be a boolean parameter")
        except KeyError:
            self.alwaysOnTop = False
            
        try:
            self.permissions = self.completeJson['permissions']
            if type(self.permissions) != list:
                raise QTWSConfigException("The parameter permissions should be a list parameter")
        except KeyError:
            self.alwaysOnTop = False
            
        try:
            menu = self.completeJson['menu']
            if type(menu) != list:
                raise QTWSConfigException("The menu should be a list parameter")
            self.menu = list()
            for value in menu:
                try:
                    self.menu.append(QTWSMenuItemInfo(value))
                except KeyError:
                    raise QTWSConfigException("The menu item " + str(value) + " contains an error.")
        except KeyError:
            self.menu = list()
        
        try:
            plugins = self.completeJson['plugins']
            if type(plugins) != list:
                raise QTWSConfigException("The plugins should be a list parameter")
            self.plugins = list()
            for value in plugins:
                self.plugins.append(QTWSPluginInfo(value))
        except KeyError:
            self.plugins = list()
        
    def isInScope(self, url):
        if type(url) == QUrl: 
            url = url.toString()
            
        for scope in self.scope:
            if re.search(scope, url) != None:
                return True
            
        return False
    
    def hasPermission(self, permission):
        return False
        
class QTWSConfigException(RuntimeError):
    def __init__(self, arg):
      self.args = arg
      
class QTWSPluginInfo:
    def __init__(self, entry):
        self.name = entry["name"]
        self.params = dict()
        for key, value in entry.items():
            if key != "name":
                self.params[key] = value
                
    def getParam(self, param):
        try:
            return self.params[param]
        except:
            return None

class QTWSMenuItemInfo:
    def __init__(self, entry):
        self.title      = entry['title']
        self.action     = QUrl(entry['action'])
        
        if 'icon' in entry.keys():
            self.icon = entry['icon']
        else:
            self.icon = None
            
        if 'separator' in entry.keys():
            self.separator  = entry['separator']
        else:
            self.separator = False
