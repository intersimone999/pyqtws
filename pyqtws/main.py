#!/usr/bin/env python

import sys
import subprocess
import logging
import time

from argparse import ArgumentParser
from urllib.parse import urlparse

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QSettings

from folder_manager import QTWSFolderManager, NoHomeFolderError
from silo_window import QTWSMainWindow
from options_window import QTWSOptionsWindow
from chooser_window import QTWSChooserWindow
from config import QTWSConfig
from plugins import QTWSPluginManager

import browser as external_browser

def __app_path():
    print(QTWSFolderManager.apps_folder())
    return 0


def __find_app_by_url(url: str):    
    parsed_url = urlparse(url)
    if parsed_url.scheme == "silo":
        if parsed_url.hostname == "start":
            return (parsed_url.fragment, parsed_url.username)
        elif parsed_url.hostname == "choose":
            return ("appChooser", None)

    for app_config in QTWSFolderManager.all_apps():
        conf = QTWSConfig(app_config)
        if conf.in_scope(url):
            return (app_config.split("/")[-1].replace('.qtws', ''), None)

    return (None, None)


if __name__ == '__main__':
    parser = ArgumentParser(description='The new web.')
    
    parser.add_argument(
        '-a', '--app', 
        help='opens the specified app', 
        required=False
    )
    
    parser.add_argument(
        '-f', '--appfile', 
        help='opens the specified app file', 
        required=False
    )
    
    parser.add_argument(
        '-r', '--root', 
        help='specifies the root apps folder for silos', 
        required=False
    )
    
    parser.add_argument(
        '-P', '--profile', 
        help='profile to use', 
        required=False
    )
    
    parser.add_argument(
        '-p', '--plugin', 
        help='QT plugins to enable', 
        required=False
    )
    
    parser.add_argument(
        '-o', '--options', 
        help='open the options window', 
        required=False, action='store_const', const='c'
    )
    
    parser.add_argument(
        '-A', '--path', 
        help='prints the path to the app folder in the local system', 
        action='store_const', required=False, const='c'
    )
    
    parser.add_argument(
        '--debug', 
        help='enables debugging', 
        action='store_const', required=False, const='c'
    )
    
    parser.add_argument(
        'url', 
        help='opens the specified URL with the correct app', 
        nargs='?'
    )

    args = parser.parse_args()
    app_id = args.app
    profile = args.profile
    
    if args.debug:
        logname = f"silo.{time.time()}.log"
        print(f"Running in debug mode. Saving info to {logname}")
        logging.basicConfig(filename=logname)
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        if args.root:
            QTWSFolderManager.setup([args.root])
        else:
            QTWSFolderManager.setup()
    except NoHomeFolderError:
        app = QApplication(["silos"])
        QMessageBox().critical(
            None, 
            'No apps available', 
            'No app paths available on your system.', 
            QMessageBox.StandardButton.Ok
        )
        ex = QTWSOptionsWindow()
        sys.exit(app.exec())
    
    if args.path:
        sys.exit(__app_path())
    
    if args.options:
        app = QApplication(["silos"])
        ex = QTWSOptionsWindow()
        sys.exit(app.exec())

    if not app_id:
        if args.url:
            app_id, profile = __find_app_by_url(args.url)
            if not app_id:
                url = args.url.replace("silo://", "https://")
                external_browser.open(url)
                sys.exit(0)
        else:
            app_id = "appChooser"

    if app_id and app_id.lower() == "appchooser":
        app = QApplication(["silos"])
        ex = QTWSChooserWindow(QTWSFolderManager.apps_folder())
        sys.exit(app.exec())

    if app_id:
        app_id = app_id.lower()
        app_path = None
        if args.appfile:
            app_path = args.appfile
        else:
            app_path = QTWSFolderManager.app_file(app_id)
        
        config = QTWSConfig(app_path, app_id)
        QTWSPluginManager.instance().load_plugins(config)
        
        app = QApplication([f"silos-{app_id}"])
        QTWSPluginManager.instance().each(
            lambda plugin: plugin.app_setup(app)
        )
        
        ex = QTWSMainWindow(app_id, app_path, args.url, profile=profile)
        sys.exit(app.exec())
    else:
        print("Invalid silo command")
        sys.exit(-1)
