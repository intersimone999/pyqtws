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
from urllib.parse import urlparse

__home__ = os.path.dirname(os.path.realpath(__file__))
__app_folder__ = "apps"


def warn(message: str):
    print(message, file=sys.stderr)


def __install_service(fname: str):
    app_id = os.path.basename(fname).replace(".qtws", "")

    if " " in app_id or not app_id.islower():
        warn("The name of a service file must be in lowercase and it must contain no whitespaces.")
        return -1
    if os.path.exists(fname):
        try:
            config = QTWSConfig(fname)
            print("Do you want to install the following service?")
            print("Name: " + config.name)
            print("Description: " + config.description)
            print("Scope: " + str.join(", ", config.scope))

            problems = config.problems()
            if len(problems) > 0:
                print("Warning:")
            for problem in problems:
                print("\t" + problems)

            answer = None
            while not answer or answer not in ['y', 'n']:
                answer = input("Do you want to install this service? (y/n)").lower()

            if answer == 'y':
                dest_fname = os.path.join(__home__, "apps/" + app_id + ".qtws")
                try:
                    with open(fname) as in_file:
                        with open(dest_fname, "w") as out_file:
                            out_file.write(in_file.read())
                except Exception as e:
                    warn("The service could not be installed: " + str(e))
                    return -1

                return 0
            else:
                print("Aborted")
                return 0

        except:
            warn("The specified file does not seem to be a valid service file.")

    else:
        warn("The specified file does not exist.")
        return -1


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
    parser.add_argument('-p', '--plugin', help='QT plugins to enable', required=False)
    parser.add_argument('-i', '--install', help='install the specified file', required=False)
    parser.add_argument('url', help='opens the specified URL with the correct app', nargs='?')

    args = parser.parse_args()
    app_id = args.app
    
    if args.install:
        sys.exit(__install_service(args.install))

    if not app_id:
        if args.url:
            app_id = __find_app_by_url(args.url)
            if not app_id:
                url = args.url.replace("silo://", "https://")
                webbrowser.open(url)
                sys.exit(0)
        else:
            app_id = "appChooser"

    app_chooser = None
    if app_id and app_id.lower() == "appchooser":
        app_chooser = AppChooser(os.path.join(__home__, __app_folder__, "appChooser"))
        app_chooser.start_serving()

    if app_id:
        app_id = app_id.lower()
        app_path = os.path.join(__home__, __app_folder__, app_id + ".qtws")
        config = QTWSConfig(app_path)

        app = QApplication(["silos"])
        ex = QTWSMainWindow(app_id, app_path, args.url, app_chooser)
        sys.exit(app.exec_())
    else:
        print("Invalid silo command")
        sys.exit(-1)
