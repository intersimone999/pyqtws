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
from config import *
from urllib.parse import urlparse

__home__ = os.path.dirname(os.path.realpath(__file__))
__app_folder__ = "apps"


def warn(message: str):
    print(message, file=sys.stderr)


def __app_path():
    print(os.path.realpath(__file__).replace(__file__, "") + "apps")
    return 0


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
    parser.add_argument('-f', '--appfile', help='opens the specified app file', required=False)
    parser.add_argument('-p', '--plugin', help='QT plugins to enable', required=False)
    parser.add_argument('-i', '--install', help='install the specified file', required=False)
    parser.add_argument('-o', '--options', help='open the options window', required=False, action='store_const', const='c')
    parser.add_argument('-A', '--path', help='prints the path to the app folder in the local system', action='store_const', required=False, const='c')
    parser.add_argument('url', help='opens the specified URL with the correct app', nargs='?')

    args = parser.parse_args()
    app_id = args.app
    
    if args.install:
        sys.exit(__install_service(args.install))
        
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

    app_chooser = None
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
        ex = QTWSMainWindow(app_id, app_path, args.url, app_chooser)
        sys.exit(app.exec_())

    else:
        print("Invalid silo command")
        sys.exit(-1)
