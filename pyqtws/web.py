import webbrowser
import logging
import os
import time

from PyQt6.QtCore import Qt
from PyQt6.QtCore import QPoint
from PyQt6.QtCore import QUrl
from PyQt6.QtCore import QDir
from PyQt6.QtCore import QFileInfo
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMenu, QWidget
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from PyQt6.QtWidgets import QGridLayout
from PyQt6.QtWidgets import QProgressBar, QPushButton, QLabel
from PyQt6.QtGui import QAction
from PyQt6.QtGui import QIcon
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtWebEngineWidgets import QWebEngineView

from config import QTWSConfig
from plugins import QTWSPluginManager
from permissions import QTWSPermissionManager

import browser as external_browser


class QTWSWebView(QWebEngineView):
    def __init__(self):
        super().__init__()
        
    def initialize(self, config: QTWSConfig, window, profile_name: str = None):
        self.config = config
        self.window = window
        
        candidate_profiles = [profile_name]
        QTWSPluginManager.instance().each(
            lambda plugin: plugin.web_profile_candidate(candidate_profiles)
        )
        
        if len(candidate_profiles) >= 1:
            profile_name = candidate_profiles[0]
        
        if profile_name is None or profile_name.lower() == 'default':
            self.profile = QWebEngineProfile("default")
        else:
            self.profile = QWebEngineProfile(profile_name)
        
        maxCache = self.config.cache_mb * 1024 * 1024
        self.profile.setHttpCacheMaximumSize(maxCache)
        
        self.profile.downloadRequested.connect(
            lambda item: self.__download(item)
        )
        
        QTWSPluginManager.instance().each(
            lambda plugin: plugin.web_profile_setup(self.profile)
        )
        
        self.webPage = QTWSWebPage(self.config, self.profile)
        self.setPage(self.webPage)
        self.permission_manager = QTWSPermissionManager(self.webPage)
        
        QTWSPluginManager.instance().each(
            lambda plugin: plugin.web_engine_setup(self)
        )

        if self.config.menu_disabled:
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        else:
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.customContextMenuRequested.connect(self.__show_menu)

        self.__create_actions()

        self.urlChanged.connect(self.__url_changed)

        self.settings().setAttribute(
            QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, 
            True
        )
        self.settings().setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, 
            True
        )
        self.settings().setAttribute(
            QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, 
            True
        )
        self.settings().setAttribute(
            QWebEngineSettings.WebAttribute.PluginsEnabled, 
            True
        )
        
        self.download_windows = []
        
    def grant_permission(self, permission):
        self.permission_manager.grant_permission(permission)

    def __create_actions(self):
        self.__actionBack = QAction(
            QIcon.fromTheme("back"), 
            "Back"
        )
        self.__actionBack.triggered.connect(
            lambda: self.back()
        )

        self.__actionReload = QAction(
            QIcon.fromTheme("reload"), 
            "Reload"
        )
        self.__actionReload.triggered.connect(
            lambda: self.reload()
        )

        self.__actionHome = QAction(
            QIcon.fromTheme("go-home"),
            "Home"
        )
        self.__actionHome.triggered.connect(
            lambda: self.setUrl(self.config.home)
        )

        self.__actionShare = QAction(
            QIcon.fromTheme("emblem-shared"),
            "Share"
        )
        self.__actionShare.triggered.connect(
            self.__share
        )
        
        self.__actionOpenBrowser = QAction(
            QIcon.fromTheme("internet-web-browser"),
            "Open in the browser"
        )
        self.__actionOpenBrowser.triggered.connect(
            self.__open_in_browser
        )

        self.__actionQuit = QAction(
            QIcon.fromTheme("application-exit"),
            "Quit"
        )
        self.__actionQuit.triggered.connect(
            self.__quit
        )

        self.__customActions = list()
        for menu_item in self.config.menu:
            if menu_item.icon:
                action = QAction(
                    QIcon.fromTheme(menu_item.icon),
                    menu_item.title
                )
            else:
                action = QAction(menu_item.title)

            action.setData(menu_item.action)

            if menu_item.separator:
                self.__customActions.append("-")

            self.__customActions.append(action)

    def __show_menu(self, position: QPoint):
        self.menu = QMenu()

        if not self.page().history().canGoBack():
            self.__actionBack.setEnabled(False)
        self.menu.addAction(self.__actionBack)
        self.menu.addAction(self.__actionReload)
        self.menu.addAction(self.__actionHome)
        self.menu.addAction(self.__actionShare)
        self.menu.addAction(self.__actionOpenBrowser)

        if len(self.__customActions) > 0:
            self.menu.addSeparator()

        for action in self.__customActions:
            if action == '-':
                self.menu.addSeparator()
            else:
                self.menu.addAction(action)

        self.menu.addSeparator()

        for plugin in QTWSPluginManager.instance().plugins:
            plugin.add_menu_items(self.menu)
            self.menu.addSeparator()

        self.menu.addAction(self.__actionQuit)

        # Handles all the custom actions using the 
        # URL stored in the action's data field
        self.menu.triggered.connect(self.__menu_click)
        self.menu.popup(self.mapToGlobal(position))
        
    def __download(self, item):
        default_path = QDir(
            item.downloadDirectory()
        ).filePath(
            item.downloadFileName()
        )
        
        path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save as", 
            default_path
        )
        
        if path is None or len(path) == 0:
            item.cancel()
            return
        
        info = QFileInfo(path)
        item.setDownloadDirectory(info.dir().path())
        item.setDownloadFileName(info.fileName())
        item.accept()
        self.download_windows.append(
            DownloadProgressWindow(
                item, 
                info.dir().path() + "/" + info.fileName()
            )
        )

    def __share(self):
        QApplication.instance().clipboard().setText(self.url().toString())
        QMessageBox().information(
            self, 
            'Shared', 
            'Copied to the clipboard', 
            QMessageBox.StandardButton.Ok
        )
        
    def __open_in_browser(self):
        external_browser.open(self.url().toString())

    def __quit(self):
        self.window.quit()

    def __menu_click(self, action: QAction):
        if action.data():
            self.setUrl(action.data())

    def __url_changed(self, status):
        QTWSPluginManager.instance().each(
            lambda plugin: plugin.on_page_loaded(self.url())
        )


class QTWSWebPage(QWebEnginePage):
    def __init__(self, config: QTWSConfig, profile: QWebEngineProfile):
        super().__init__(profile, None)
        self.profile = profile
        self.config = config
        self._last_request = None
        self._last_request_time = None

    def createWindow(self, t):
        fake_page = QWebEnginePage(self.profile, self)
        fake_page.urlChanged.connect(
            lambda url: self.__create_window_request(
                fake_page, 
                url
            )
        )

        return fake_page

    def acceptNavigationRequest(
        self,
        url: QUrl, 
        request_type, 
        is_main_frame: bool
    ):
        if request_type != QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            return True

        if not is_main_frame:
            return True

        if not self.__check_in_scope(url):
            self.__open_outside_url(url)
            return False
        else:
            return True

    def __create_window_request(self, fake_page: QWebEnginePage, url: QUrl):
        if not self.__check_in_scope(url):
            if url.scheme != 'about' and url.scheme != "":
                self.__open_outside_url(url)
                return False
        else:
            self.setUrl(url)
            return False
        
    def __open_outside_url(self, url):
        silo_url = url.toString()
        silo_url = silo_url.replace("https://", "silo://")
        silo_url = silo_url.replace("http://", "silo://")
        
        base_url = f"{url.scheme()}://{url.host()}{url.path()}"
        if self._last_request != base_url or self._last_request_time - time.time() > 3:
            logging.info(
                f"Going outside because of {url.toString()}: "
                f"redirecting to {silo_url}"
            )
            webbrowser.open(silo_url)
        else:
            logging.info(
                f"Avoiding repeated opening of the same document"
            )
        
        self._last_request = base_url
        self._last_request_time = time.time()

    def __check__blacklisted(self, url: QUrl):
        for plugin in QTWSPluginManager.instance().plugins:
            if plugin.is_url_blacklisted(url):
                return True

        return False

    def __check_whitelisted(self, url: QUrl):
        for plugin in QTWSPluginManager.instance().plugins:
            if plugin.is_url_whitelisted(url):
                return True

        return False

    def __check_in_scope(self, url: QUrl):
        if self.__check_whitelisted(url):
            return True

        url_out_of_scope = not self.config.in_scope(url)
        plugin_blacklist = self.__check__blacklisted(url)
        if url_out_of_scope or plugin_blacklist:
            return False
        else:
            return True


class DownloadProgressWindow(QWidget):
    def __init__(self, download, result_path):
        super().__init__()
        
        self.download = download
        self.result_path = result_path
        self.__init_ui()
        
        self.download.receivedBytesChanged.connect(
            lambda: self.__update(self.download.receivedBytes(), self.download.totalBytes())
        )
        self.download.isFinishedChanged.connect(
            lambda: self.__completed()
        )

    def __init_ui(self):
        self.setWindowTitle("Download")
        
        self.layout = QGridLayout()
        
        self.label = QLabel(f"Downloading {self.download.downloadFileName()}...", self)
        self.progress_bar = QProgressBar()
        
        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self.progress_bar, 1, 0)
        self.layout.addWidget(self.__build_action_buttons_group(), 1, 1)
        self.layout.setContentsMargins(10, 5, 10, 5)
        
        self.setLayout(self.layout)
        
        self.show()
        
    def __build_action_buttons_group(self):
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(lambda: self.__on_cancel())
        
        self.action_buttons_layout = QGridLayout()
        self.action_buttons_layout.addWidget(self.cancel_button, 0, 0)
        
        result = QWidget()
        result.setLayout(self.action_buttons_layout)
        
        return result
    
    def __update(self, done, total):
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(done)
    
    def __completed(self):
        self.label.setText("Download completed!")
        self.cancel_button.setText("Open")
        self.cancel_button.clicked.connect(lambda: self.__on_open())
    
    def __on_open(self):
        outpath = f"file://{self.result_path}"
        webbrowser.open(outpath)
    
    def __on_cancel(self):
        if not self.download.isFinished():
            self.download.cancel()
        
        self.close()
