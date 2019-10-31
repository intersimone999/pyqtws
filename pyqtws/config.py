import json
import re

from PyQt5.QtCore import QUrl


class QTWSConfig:
    def __init__(self, config_filename: str, app_id: str = None):
        with open(config_filename) as f:
            self.complete_json = json.load(f)

        self.app_id = app_id
        self.name: str = ""
        self.description: str = ""
        self.scope: list = list()
        self.home: str = ""
        self.icon: str = ""
        self.cache_mb: int = 0
        self.save_session: bool = False
        self.menu_disabled: bool = False
        self.always_on_top: bool = False
        self.permissions: list = list()
        self.menu: list = list()
        self.plugins: list = list()

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
            self.description = self.complete_json['description']
            if type(self.description) != str:
                raise QTWSConfigException("The parameter description should be a string parameter")
        except KeyError:
            self.description = ""

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
            self.cache_mb = self.complete_json['cacheMB']
            if type(self.cache_mb) != int:
                raise QTWSConfigException("The parameter cacheMB should be an integer parameter")
        except KeyError:
            self.cache_mb = 50

        try:
            self.save_session = self.complete_json['saveSession']
            if type(self.save_session) != bool:
                raise QTWSConfigException("The parameter saveSession should be a boolean parameter")
        except KeyError:
            self.save_session = False

        try:
            self.menu_disabled = self.complete_json['menuDisabled']
            if type(self.menu_disabled) != bool:
                raise QTWSConfigException("The parameter menuDisabled should be a boolean parameter")
        except KeyError:
            self.menu_disabled = False

        try:
            self.always_on_top = self.complete_json['alwaysOnTop']
            if type(self.always_on_top) != bool:
                raise QTWSConfigException("The parameter alwaysOnTop should be a boolean parameter")
        except KeyError:
            self.always_on_top = False

        try:
            self.permissions = self.complete_json['permissions']
            if type(self.permissions) != list:
                raise QTWSConfigException("The parameter permissions should be a list parameter")
        except KeyError:
            self.permissions = list()

        try:
            menu = self.complete_json['menu']
            if type(menu) != list:
                raise QTWSConfigException("The menu should be a list parameter")
            self.menu: list = list()
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
