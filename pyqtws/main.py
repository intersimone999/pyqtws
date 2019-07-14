#!/usr/bin/env python

import sys
import webbrowser
import glob
import os
from argparse import ArgumentParser

from PyQt5.QtWidgets import QApplication

from mainwindow import QTWSMainWindow
from config import *
from appchooser import AppChooser

__home__ = os.path.dirname(os.path.realpath(__file__))
__app_folder__ = "apps"


def find_app_by_url(url: str):
    global __home__
    global __app_folder__

    for app_config in glob.iglob(os.path.join(__home__, __app_folder__, '*.qtws')):
        conf = QTWSConfig(app_config)
        if conf.in_scope(url):
            return app_config.split("/")[-1].replace('.qtws', '')

    return None


if __name__ == '__main__':
    parser = ArgumentParser(description='The new web.')
    parser.add_argument('-a', '--app', help='opens the specified app', required=False)
    parser.add_argument('url', help='opens the specified URL with the correct app', nargs='?')

    args = parser.parse_args()
    app_id = args.app

    if not app_id:
        if args.url:
            app_id = find_app_by_url(args.url)
            if not app_id:
                webbrowser.open(args.url)
                sys.exit(0)
        else:
            app_id = "appChooser"

    app_chooser = None
    if app_id == "appChooser":
        app_chooser = AppChooser(os.path.join(__home__, __app_folder__, "appChooser"))
        app_chooser.start_serving()

    if app_id:
        app_id = app_id.lower()
        app_path = os.path.join(__home__, __app_folder__, app_id + ".qtws")
        app = QApplication(sys.argv)
        ex = QTWSMainWindow(app_id, app_path, args.url, app_chooser)
        sys.exit(app.exec_())
