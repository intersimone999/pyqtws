import json
import re
import os

from PyQt5.QtCore import QUrl


class QTWSConfig:
    def __init__(self, config_filename: str, app_id: str = None):
        with open(config_filename) as f:
            self.complete_json = json.load(f)
        
        self.config_filename = config_filename
        self.app_id = app_id
        self.name: str = ""
        self.description: str = ""
        self.scope: list = list()
        self.home: str = ""
        self.icon: str = ""
        self.cache_mb: int = 50
        self.save_session: bool = False
        self.menu_disabled: bool = False
        self.always_on_top: bool = False
        self.permissions: list = list()
        self.menu: list = list()
        self.plugins: list = list()

        self.__load_data()

    def __load_data(self):
        if 'name' in self.complete_json:
            self.name = self.complete_json['name']
            if type(self.name) != str:
                raise QTWSConfigException("The parameter name should be a string parameter")
            if "/" in self.name or "//" in self.name:
                raise QTWSConfigException("Illegal name " + self.name + ": it cannot contain slashes or backslashes.")
        else:
            raise QTWSConfigException("Cannot find the name in the configuration file")

        if 'description' in self.complete_json:
            self.description = self.complete_json['description']
            if type(self.description) != str:
                raise QTWSConfigException("The parameter description should be a string parameter")
        else:
            self.description = ""

        if 'scope' in self.complete_json:
            self.scope = self.complete_json['scope']
            if type(self.scope) != list:
                raise QTWSConfigException("The scope should be an array")
        else:
            raise QTWSConfigException("Cannot find the scope in the configuration file")

        if 'home' in self.complete_json:
            self.home = self.complete_json['home']
            if type(self.home) != str:
                raise QTWSConfigException("The parameter home should be a string parameter")

            self.home = QUrl(self.home)
        else:
            raise QTWSConfigException("Cannot find the home in the configuration file")

        if 'icon' in self.complete_json:
            self.icon = self.complete_json['icon']
            if type(self.icon) != str:
                raise QTWSConfigException("The parameter icon should be a string parameter")
            else:
                self.icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.icon)
        else:
            raise QTWSConfigException("Cannot find the icon in the configuration file")

        if 'cacheMB' in self.complete_json:
            self.cache_mb = self.complete_json['cacheMB']
            if type(self.cache_mb) != int:
                raise QTWSConfigException("The parameter cacheMB should be an integer parameter")

        if 'saveSession' in self.complete_json:
            self.save_session = self.complete_json['saveSession']
            if type(self.save_session) != bool:
                raise QTWSConfigException("The parameter saveSession should be a boolean parameter")

        if 'menuDisabled' in self.complete_json:
            self.menu_disabled = self.complete_json['menuDisabled']
            if type(self.menu_disabled) != bool:
                raise QTWSConfigException("The parameter menuDisabled should be a boolean parameter")

        if 'alwaysOnTop' in self.complete_json:
            self.always_on_top = self.complete_json['alwaysOnTop']
            if type(self.always_on_top) != bool:
                raise QTWSConfigException("The parameter alwaysOnTop should be a boolean parameter")

        if 'permissions' in self.complete_json:
            self.permissions = self.complete_json['permissions']
            if type(self.permissions) != list:
                raise QTWSConfigException("The parameter permissions should be a list parameter")

        if 'menu' in self.complete_json:
            menu = self.complete_json['menu']
            if type(menu) != list:
                raise QTWSConfigException("The menu should be a list parameter")
            
            for value in menu:
                self.menu.append(QTWSMenuItemInfo(value))

        if 'plugins' in self.complete_json:
            plugins = self.complete_json['plugins']
            if type(plugins) != list:
                raise QTWSConfigException("The plugins should be a list parameter")
            
            for value in plugins:
                self.plugins.append(QTWSPluginInfo(value))

    def problems(self):
        problems: list = list()
        if self.description == "":
            problems.append("The given description is empty")

        if self.cache_mb <= 0:
            problems.append("The cache is disabled for this service")

        if self.always_on_top:
            problems.append("This service will be always on top")

        if not self.in_scope(self.home):
            problems.append("The home of this service is not in its scope")

        for element in self.menu:
            if not self.in_scope(element.action):
                problems.append("The menu item \"" + element.title + "\" goes out of the scope of the app")

        return problems

    def in_scope(self, url):
        if type(url) == QUrl:
            url = url.toString()
        
        # Always support silo as URL schema
        url = url.replace('silo://', 'https://')

        for scope in self.scope:
            if re.search(scope, url):
                return True

        return False

    def has_permission(self, permission: str):
        return False


class QTWSConfigException(RuntimeError):
    def __init__(self, arg):
        self.args = arg


class QTWSPluginInfo:
    def __init__(self, entry: dict):
        if 'name' not in entry:
            raise QTWSConfigException("You must specify the name for all the plugins.")
        
        self.name = entry["name"]
        self.params = dict()
        for key, value in entry.items():
            if key != "name":
                self.params[key] = value

    def get_param(self, param: str):
        if param in self.params.keys():
            return self.params[param]
        else:
            return None


class QTWSMenuItemInfo:
    def __init__(self, entry):
        if 'title' not in entry or 'action' not in entry:
            raise QTWSConfigException("The menu item " + str(entry) + " is missing the title or the action.")
        
        self.title = entry['title']
        self.action = QUrl(entry['action'])

        if 'icon' in entry:
            self.icon = entry['icon']
        else:
            self.icon = None

        if 'separator' in entry:
            self.separator = entry['separator']
        else:
            self.separator = False
