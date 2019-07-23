from PyQt5.QtWidgets import QMenu
from PyQt5.Qt import QUrl


class QTWSPlugin:
    def __init__(self, name: str):
        self.name = name

    def web_engine_setup(self, web):
        pass
    
    def web_profile_setup(self, profile):
        pass

    def window_setup(self, window):
        pass

    def on_action_clicked(self):
        pass

    def on_page_loaded(self, url: QUrl):
        pass

    def add_menu_items(self, menu: QMenu):
        pass

    def is_url_blacklisted(self, url: QUrl):
        return False

    def is_url_whitelisted(self, url: QUrl):
        return False


class QTWSPluginManager:
    __instance = None

    def __init__(self):
        self.plugins = None

    @staticmethod
    def instance():
        if not QTWSPluginManager.__instance:
            QTWSPluginManager.__instance = QTWSPluginManager()

        return QTWSPluginManager.__instance

    def load_plugins(self, config):
        self.plugins = list()
        for plugin_info in config.plugins:
            plugin_module = __import__('plugin.' + plugin_info.name, globals(), locals(), [plugin_info.name])
            plugin_instance = plugin_module.instance(config, plugin_info.params)
            self.plugins.append(plugin_instance)

    def each(self, action: callable):
        for plugin in self.plugins:
            action(plugin)
