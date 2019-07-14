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


def find_app_by_url(url: str):
    global __home__
    for appConfig in glob.iglob(os.path.join(__home__, 'apps/*.qtws')):
        conf = QTWSConfig(appConfig)
        if conf.in_scope(url):
            return appConfig.split("/")[-1].replace('.qtws', '')

    return None


if __name__ == '__main__':
    parser = ArgumentParser(description='The new web.')
    parser.add_argument('-a', '--app', help='opens the specified app', required=False)
    parser.add_argument('url', help='opens the specified URL with the correct app', nargs='?')

    args = parser.parse_args()
    qtws_app_name = args.app
    print(qtws_app_name)
    if not qtws_app_name:
        if args.url:
            qtws_app_name = find_app_by_url(args.url)
            if not qtws_app_name:
                webbrowser.open(args.url)
                sys.exit(0)
        else:
            qtws_app_name = "appChooser"

    app_chooser = None
    if qtws_app_name == "appChooser":
        app_chooser = AppChooser(os.path.join(__home__, "apps/appChooser"))
        app_chooser.start_serving()

    if qtws_app_name:
        qtws_app_name = os.path.join(__home__, "apps/" + qtws_app_name.lower() + ".qtws")
        app = QApplication(sys.argv)
        ex = QTWSMainWindow(qtws_app_name, args.url, app_chooser)
        sys.exit(app.exec_())
