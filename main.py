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

def findAppByUrl(url):
    global __home__
    for appConfig in glob.iglob(os.path.join(__home__, 'apps/*.qtws')):
        conf = QTWSConfig(appConfig)
        if conf.isInScope(url):
            return appConfig.split("/")[-1].replace('.qtws', '')
        
    return None
    
if __name__ == '__main__':
    parser = ArgumentParser(description='The new web.')
    parser.add_argument('-a', '--app',  help='opens the specified app', required=False)
    parser.add_argument('url', help='opens the specified URL with the correct app', nargs='?')

    args = parser.parse_args()
    qtwsAppName = args.app
    print(qtwsAppName)
    if not qtwsAppName:
        if args.url:
            qtwsAppName = findAppByUrl(args.url)
            if not qtwsAppName:
                webbrowser.open(args.url)
                sys.exit(0)
        else:
            qtwsAppName = "appChooser"
        
    appChooser = None
    if qtwsAppName == "appChooser":
        appChooser = AppChooser(os.path.join(__home__, "apps/appChooser"))
        appChooser.startServing()
    
    if qtwsAppName:
        qtwsAppName = os.path.join(__home__, "apps/" + qtwsAppName.lower() + ".qtws")
        app = QApplication(sys.argv)
        ex = QTWSMainWindow(qtwsAppName, args.url, appChooser)
        sys.exit(app.exec_())
