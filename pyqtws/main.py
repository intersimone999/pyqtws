#!/usr/bin/env python

import sys
import webbrowser
import glob
import os
import subprocess
from argparse import ArgumentParser

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings

from silo_window import QTWSMainWindow
from options_window import QTWSOptionsWindow
from chooser_window import QTWSChooserWindow
from config import QTWSConfig
from urllib.parse import urlparse

__home__ = os.path.dirname(os.path.realpath(__file__))
__app_folder__ = "apps"


def __app_path():
    print(os.path.realpath(__file__).replace(__file__, "") + "apps")
    return 0


def __find_app_by_url(url: str):
    global __home__
    global __app_folder__
    
    parsed_url = urlparse(url)
    if parsed_url.scheme == "silo":
        if parsed_url.netloc == "start":
            return parsed_url.fragment
        elif parsed_url.netloc == "choose":
            return "appChooser"

    for app_config in glob.iglob(os.path.join(__home__, __app_folder__, '*.qtws')):
        conf = QTWSConfig(app_config)
        if conf.in_scope(url):
            return app_config.split("/")[-1].replace('.qtws', '')

    return None


if __name__ == '__main__':
    parser = ArgumentParser(description='The new web.')
    parser.add_argument('-a', '--app', help='opens the specified app', required=False)
    parser.add_argument('-f', '--appfile', help='opens the specified app file', required=False)
    parser.add_argument('-p', '--plugin', help='QT plugins to enable', required=False)
    parser.add_argument('-o', '--options', help='open the options window', required=False, action='store_const', const='c')
    parser.add_argument('-A', '--path', help='prints the path to the app folder in the local system', action='store_const', required=False, const='c')
    parser.add_argument('url', help='opens the specified URL with the correct app', nargs='?')

    args = parser.parse_args()
    app_id = args.app
    
    if args.path:
        sys.exit(__app_path())
    
    if args.options:
        app = QApplication(["silos"])
        ex = QTWSOptionsWindow()
        sys.exit(app.exec_())

    if not app_id:
        if args.url:
            app_id = __find_app_by_url(args.url)
            if not app_id:
                url = args.url.replace("silo://", "https://")
                silo_options = QSettings("silos", "Options")
                default_browser = silo_options.value("browser/defaultBrowser")
                if default_browser is None:
                    app = QApplication(["silos"])
                    ex = QTWSOptionsWindow(True)
                    app.exec_()
                
                silo_options = QSettings("silos", "Options")
                default_browser = silo_options.value("browser/defaultBrowser")
                subprocess.call([default_browser, url])
                sys.exit(0)
        else:
            app_id = "appChooser"

    if app_id and app_id.lower() == "appchooser":
        apps_path = os.path.join(__home__, __app_folder__)
        app = QApplication(["silos"])
        ex = QTWSChooserWindow(apps_path)
        sys.exit(app.exec_())
        

    if app_id:
        app_id = app_id.lower()
        app_path = None
        if args.appfile:
            app_path = args.appfile
        else:
            app_path = os.path.join(__home__, __app_folder__, app_id + ".qtws")
            
        config = QTWSConfig(app_path)

        app = QApplication(["silos"])
        ex = QTWSMainWindow(app_id, app_path, args.url)
        sys.exit(app.exec_())

    else:
        print("Invalid silo command")
        sys.exit(-1)
