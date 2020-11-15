from PyQt5.QtWidgets import QMenu
from PyQt5.Qt import QUrl


class QTWSPlugin:
    def __init__(self, name: str):
        self.name = name

    def web_engine_setup(self, web):
        """
        Abstract method that allows to setup the web engine
        """
        pass
    
    def web_profile_setup(self, profile):
        """
        Abstract method that allows to setup the profile of the web engine
        """
        pass

    def window_setup(self, window):
        """
        Abstract method that allows to setup the main window
        """
        pass

    def on_page_loaded(self, url: QUrl):
        """
        Abstract method that is called every time a page is loaded
        """
        pass

    def add_menu_items(self, menu: QMenu):
        """
        Abstract method that allows to add items to the context menu
        """
        pass

    def is_url_blacklisted(self, url: QUrl):
        """
        Method that checks if the given url is blacklisted
        """
        return False

    def is_url_whitelisted(self, url: QUrl):
        """
        Method that checks if the given url is whitelisted
        """
        return False
    
    def close_event(self, window, event):
        """
        Abstract method that is called when the user closes the window
        """
        pass
    
    def register_shortcuts(self, window):
        """
        Abstract method that allows to register custom shortcuts for the plugin
        """
        pass


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
