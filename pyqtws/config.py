import json
import re

from PyQt5.QtCore import QUrl


class QTWSConfig:
    def __init__(self, config_filename: str, app_id: str = None):
        with open(config_filename) as f:
            self.complete_json = json.load(f)

        self.app_id = app_id
        self.__load_data()

    def __load_data(self):
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

            self.home = QUrl(self.home)
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
            if type(self.menuDisabled) != bool:
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

    def in_scope(self, url):
        if type(url) == QUrl:
            url = url.toString()

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
        self.title = entry['title']
        self.action = QUrl(entry['action'])

        if 'icon' in entry.keys():
            self.icon = entry['icon']
        else:
            self.icon = None

        if 'separator' in entry.keys():
            self.separator = entry['separator']
        else:
            self.separator = False
