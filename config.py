import json
import re

class QTWSConfigParser:
    def __init__(self, config_filename):
        with open(config_filename) as f:
            self.complete_json = json.load(f)
        self.__loadData()

    def __loadData(self):
        try:
            self.name = self.complete_json['name']
            if type(self.name) != str:
                raise QTWSConfigException("The parameter name should be a string parameter")
            if "/" in self.name or "//" in self.name:
                raise QTWSConfigException("Illegal name " + self.name + ": it cannot contain slashes or backslashes.")
        except KeyError:
            raise QTWSConfigException("Cannot find the name in the configuration file")
        
        try:
            self.scope = self.complete_json['scope']
            if type(self.scope) != list:
                raise QTWSConfigException("The scope should be an array")
        except KeyError:
            raise QTWSConfigException("Cannot find the scope in the configuration file")
        
        try:
            self.home = self.complete_json['home']
            if type(self.home) != str:
                raise QTWSConfigException("The parameter home should be a string parameter")
        except KeyError:
            raise QTWSConfigException("Cannot find the home in the configuration file")
        
        try:
            self.icon = self.complete_json['icon']
            if type(self.icon) != str:
                raise QTWSConfigException("The parameter icon should be a string parameter")
        except KeyError:
            raise QTWSConfigException("Cannot find the icon in the configuration file")
        
        try:
            self.cacheMB = self.complete_json['cacheMB']
            if type(self.cacheMB) != int:
                raise QTWSConfigException("The parameter cacheMB should be an integer parameter")
        except KeyError:
            self.cacheMB = 50
        
        try:
            self.saveSession = self.complete_json['saveSession']
            if type(self.saveSession) != bool:
                raise QTWSConfigException("The parameter saveSession should be a boolean parameter")
        except KeyError:
            self.saveSession = False
            
        try:
            self.menuDisabled = self.complete_json['menuDisabled']
            if type(self.alwaysOnTop) != bool:
                raise QTWSConfigException("The parameter menuDisabled should be a boolean parameter")
        except KeyError:
            self.menuDisabled = False
            
        try:
            self.alwaysOnTop = self.complete_json['alwaysOnTop']
            if type(self.alwaysOnTop) != bool:
                raise QTWSConfigException("The parameter alwaysOnTop should be a boolean parameter")
        except KeyError:
            self.alwaysOnTop = False
            
        try:
            self.permissions = self.complete_json['permissions']
            if type(self.permissions) != list:
                raise QTWSConfigException("The parameter permissions should be a list parameter")
        except KeyError:
            self.alwaysOnTop = False
            
        try:
            menu = self.complete_json['menu']
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
            plugins = self.complete_json['plugins']
            if type(plugins) != list:
                raise QTWSConfigException("The plugins should be a list parameter")
            self.plugins = list()
            for value in plugins:
                self.plugins.append(QTWSPluginInfo(value))
        except KeyError:
            self.plugins = list()
        
    def isInScope(self, url):
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
        self.action     = entry['action']
        self.icon       = entry['icon']
        self.separator  = entry['separator']
