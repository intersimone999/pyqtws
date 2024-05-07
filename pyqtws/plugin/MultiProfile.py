from config import QTWSConfig
from plugins import QTWSPlugin
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QSettings, QSize
from PyQt6.QtGui import QShortcut, QAction, QIcon
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QMenu
from PyQt6.QtWidgets import QPushButton, QLineEdit, QLabel
from PyQt6.QtWidgets import QGridLayout
from PyQt6.QtWidgets import QInputDialog, QMessageBox
from PyQt6.QtWidgets import QApplication

from folder_manager import QTWSFolderManager
from silo_window import QTWSMainWindow

import webbrowser
import hashlib


class MultiProfile(QTWSPlugin):
    def __init__(self, config):
        super().__init__("MultiProfile")
        self.config = config
        self.profile_manager = None
    
    def window_setup(self, window):
        self.window = window
            
        self.settings = QSettings(self.config.name, "MultiProfile", window)
        self.__load_profiles()
        
        window.setWindowTitle(f"{self.config.name} @ {self.active_profile.name}")
    
    def add_menu_items(self, menu: QMenu):
        self.switch_profile_actions = []
    
        self.profile_manager_action = QAction(
            QIcon.fromTheme("user"),
            "Switch profile"
        )
        self.profile_manager_action.triggered.connect(
            lambda: self.__show_profile_manager()
        )
        menu.addAction(self.profile_manager_action)
        
    def switch_profile(self, profile, app_id):
        self.window.reset(app_id, QTWSFolderManager.app_file(app_id), profile=profile.name)
    
    def register_shortcuts(self, window):
        self.__keyCtrlP = QShortcut(window)
        self.__keyCtrlP.setKey("Ctrl+P")
        self.__keyCtrlP.activated.connect(lambda: self.__show_profile_manager())
    
    def __show_profile_manager(self):
        if self.profile_manager is None:
            self.profile_manager = ProfileManagerWindow(
                self, 
                self.config, 
                self.settings,
                self.profiles,
                self.active_profile,
            )
    
    def __load_profiles(self):
        profiles_str = self.settings.value("profiles")
        if profiles_str is not None and profiles_str:
            profiles = profiles_str.split(";")
            self.profiles = [Profile.deserialize(p) for p in profiles]
        else:
            self.profiles = []
        
        default = self.window.profile_id() is None or \
                    self.window.profile_id().lower() == 'default'
        
        self.active_profile = None
        
        if default:
            self.active_profile = Profile.default()
        else:
            for profile in self.profiles:
                if profile.id == self.window.profile_id():
                    self.active_profile = profile
        
        if self.active_profile is None:
            if self.window.profile_id() != '':
                profile_name = f"Custom ({self.window.profile_id()})"
            else:
                profile_name = "Anonymous"
            
            self.active_profile = Profile(
                self.window.profile_id(), 
                profile_name
            )
    
    def unregister_profile_manager(self):
        self.profile_manager = None


class Profile:
    MAX_NAME_SIZE = 20
    DEFAULT = None
    
    @staticmethod
    def deserialize(string):
        parts = string.split(":")
        id = parts[0]
        name = parts[1]
        return Profile(id, name)
    
    @staticmethod
    def default():
        if Profile.DEFAULT is None:
            Profile.DEFAULT = Profile('Default', 'Default')
        
        return Profile.DEFAULT
        
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    def serialize(self):
        return f"{self.id}:{self.name}"


class ProfileWidget(QWidget):
    def __init__(
        self, 
        profile_manager, 
        config, 
        profile, 
        icon,
        erasable=False,
        active=False
    ):
        super().__init__()
        self.profile_manager = profile_manager
        
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
        
        self.button = QPushButton("Use")
        self.button.setIcon(QIcon.fromTheme('system-switch-user'))
        self.button.setStyleSheet(
            "QPushButton { text-align: left; padding: 8px; }"
        )
        self.button.setEnabled(not active)
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
        self.profile_manager.plugin.switch_profile(self.profile, self.config.app_id)
        self.profile_manager.close()
    
    def delete(self):
        self.profile_manager.delete_profile(self)


class ProfileManagerWindow(QWidget):
    def __init__(self, plugin, config, settings, profiles, active):
        super().__init__()
        self.plugin = plugin
        self.config = config
        self.settings = settings
        self.profiles = profiles
        self.active_profile = active
        
        self.__init_ui()
    
    def delete_profile(self, widget):
        self.profiles.remove(widget.profile)
        self.layout.removeWidget(widget)
        widget.hide()
        self.save()
        
    def __init_ui(self):
        self.setWindowTitle("Choose profile")
        
        self.layout = QGridLayout()
        
        for profile in self.profiles:
            active = self.active_profile == profile
            widget = ProfileWidget(
                profile_manager=self,
                config=self.config,
                profile=profile,
                icon=QIcon.fromTheme("user"),
                erasable=(not active),
                active=active
            )
            self.layout.addWidget(widget)
            
        widget = ProfileWidget(
            profile_manager=self, 
            config=self.config, 
            profile=Profile("anonymous", "Anonymous"), 
            icon=QIcon.fromTheme("view-hidden")
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
            QLineEdit.EchoMode.Normal, 
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
                    QMessageBox.StandardButton.Ok
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
                    QMessageBox.StandardButton.Ok
                )
                return
            elif profile_name in map(lambda e: e.name, self.profiles):
                QMessageBox().critical(
                    self, 
                    'Profile already existing', 
                    'A profile with this name already exists.', 
                    QMessageBox.StandardButton.Ok
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
                    profile_manager=self, 
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
        self.plugin.unregister_profile_manager()


def instance(config: QTWSConfig, params: dict):
    return MultiProfile(config)
