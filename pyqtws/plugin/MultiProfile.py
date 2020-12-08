from config import QTWSConfig
from plugins import QTWSPlugin
from PyQt5.QtCore import QSettings, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QInputDialog, QMessageBox

import webbrowser
import hashlib


class MultiProfile(QTWSPlugin):
    def __init__(self, config):
        super().__init__("MultiProfile")
        self.config = config
        self.profile_chooser = None
    
    def window_setup(self, window):
        self.window = window
        self.settings = QSettings(self.config.name, "MultiProfile", window)
    
    def add_menu_items(self, menu: QMenu):
        self.switch_profile_action = QAction(
            QIcon.fromTheme("user"),
            "Switch profile"
        )
        self.switch_profile_action.triggered.connect(
            lambda: self.__switch_profile()
        )
        menu.addAction(self.switch_profile_action)
    
    def __switch_profile(self):
        if self.profile_chooser is None:
            self.profile_chooser = ProfileChooserWindow(
                self, 
                self.config, 
                self.settings
            )
    
    def unregister_chooser_window(self):
        self.profile_chooser = None


class Profile:
    MAX_NAME_SIZE = 20
    
    @staticmethod
    def deserialize(string):
        parts = string.split(":")
        id = parts[0]
        name = parts[1]
        return Profile(id, name)
        
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    def serialize(self):
        return f"{self.id}:{self.name}"


class ProfileWidget(QWidget):
    def __init__(self, profile_chooser, config, profile, icon, erasable=False):
        super().__init__()
        self.profile_chooser = profile_chooser
        
        self.config = config
        self.profile = profile
        self.erasable = erasable
        self.layout = QGridLayout()
        
        self.can_open = True
        
        self.icon = QLabel(profile.name)
        self.icon.setMaximumWidth(20)
        self.icon.setPixmap(icon.pixmap(icon.actualSize(QSize(20, 20))))
        self.layout.addWidget(self.icon, 0, 0)
        
        self.label = QLabel(profile.name)
        self.label.setStyleSheet("QLabel { min-width: 20em; }")
        self.layout.addWidget(self.label, 0, 1)
        
        self.button = QPushButton("Switch")
        self.button.setIcon(QIcon.fromTheme('system-switch-user'))
        self.button.setStyleSheet(
            "QPushButton { text-align: left; padding: 8px; }"
        )
        self.clicked = self.button.clicked
        self.clicked.connect(lambda: self.switch_profile())
        self.layout.addWidget(self.button, 0, 2)
        
        if self.erasable:
            self.erase = QPushButton("Delete")
            self.erase.setIcon(QIcon.fromTheme('delete'))
            self.erase.setStyleSheet(
                "QPushButton { text-align: left; padding: 8px; }"
            )
            self.erase.clicked.connect(lambda: self.delete())
            self.layout.addWidget(self.erase, 0, 3)
        
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.setLayout(self.layout)
        self.show()
    
    def switch_profile(self):
        if self.profile.id == 'default':
            webbrowser.open(
                f"silo://start#{self.config.app_id}"
            )
        elif self.profile.id == 'anonymous':
            webbrowser.open(
                f"silo://@start#{self.config.app_id}"
            )
        else:
            webbrowser.open(
                f"silo://{self.profile.id}@start#{self.config.app_id}"
            )
            
        self.profile_chooser.close()
    
    def delete(self):
        self.profile_chooser.delete_profile(self)


class ProfileChooserWindow(QWidget):
    def __init__(self, plugin, config, settings):
        super().__init__()
        self.plugin = plugin
        self.config = config
        self.settings = settings
        
        profiles_str = settings.value("profiles")
        if profiles_str is not None and profiles_str:
            profiles = profiles_str.split(";")
            self.profiles = [Profile.deserialize(p) for p in profiles]
        else:
            self.profiles = []
        
        self.__init_ui()
    
    def delete_profile(self, widget):
        self.profiles.remove(widget.profile)
        self.layout.removeWidget(widget)
        widget.hide()
        self.save()
        
    def __init_ui(self):
        self.setWindowTitle("Switch profile")
        
        self.layout = QGridLayout()
        
        widget = ProfileWidget(
            profile_chooser=self, 
            config=self.config, 
            profile=Profile("default", "Default"), 
            icon=QIcon.fromTheme("user-home")
        )
        self.layout.addWidget(widget)
        
        widget = ProfileWidget(
            profile_chooser=self, 
            config=self.config, 
            profile=Profile("anonymous", "Anonymous"), 
            icon=QIcon.fromTheme("view-hidden")
        )
        self.layout.addWidget(widget)
        
        for profile in self.profiles:
            widget = ProfileWidget(
                profile_chooser=self,
                config=self.config,
                profile=profile,
                icon=QIcon.fromTheme("user"),
                erasable=True
            )
            self.layout.addWidget(widget)
        
        self.__register_add_button()
        
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.setLayout(self.layout)
        self.show()
    
    def __register_add_button(self):
        self.add_button = QPushButton("Add new profile")
        self.add_button.setIcon(QIcon.fromTheme("list-add"))
        self.add_button.clicked.connect(lambda: self.__new_profile())
        self.layout.addWidget(self.add_button)
    
    def __new_profile(self):
        profile_name, okPressed = QInputDialog.getText(
            self, 
            "Create profile", 
            "Profile name:", 
            QLineEdit.Normal, 
            ""
        )
        profile_name = profile_name.strip()
        if okPressed:
            if len(profile_name) == 0 or \
                    len(profile_name) > Profile.MAX_NAME_SIZE:
                QMessageBox().critical(
                    self, 
                    'Name not allowed', 
                    f'Empty names or names longer than '
                    f'{Profile.MAX_NAME_SIZE} characters are not allowed.', 
                    QMessageBox.Ok
                )
                return
            if ':' in profile_name or \
                    ';' in profile_name or \
                    '@' in profile_name or \
                    '=' in profile_name:
                QMessageBox().critical(
                    self, 
                    'Symbol not allowed', 
                    '":", ";", "@", and "=" are not allowed here.', 
                    QMessageBox.Ok
                )
                return
            elif profile_name in map(lambda e: e.name, self.profiles):
                QMessageBox().critical(
                    self, 
                    'Profile already existing', 
                    'A profile with this name already exists.', 
                    QMessageBox.Ok
                )
                return
            else:
                profile_id = hashlib.md5(profile_name.encode()).hexdigest()
                profile = Profile(profile_id, profile_name)
                self.profiles.append(profile)
                self.save()
                
                self.layout.removeWidget(self.add_button)
                self.add_button.hide()
                widget = ProfileWidget(
                    profile_chooser=self, 
                    config=self.config, 
                    profile=profile, 
                    icon=QIcon.fromTheme("user"), 
                    erasable=True
                )
                self.layout.addWidget(widget)
                widget.show()
                self.__register_add_button()
    
    def save(self):
        profiles = ";".join(map(lambda e: e.serialize(), self.profiles))
        self.settings.setValue("profiles", profiles)
    
    def closeEvent(self, event):
        self.plugin.unregister_chooser_window()


def instance(config: QTWSConfig, params: dict):
    return MultiProfile(config)
