#!/usr/bin/env python

import setuptools
import sys
import os
import glob

from config import QTWSConfig

HOME_PATH = os.path.dirname(os.path.realpath(__file__))

SUPPORTED_OS = ["linux"]

def make_desktop_file(app_src, desktop_dest):
    global HOME_PATH

    print("Building desktop file for " + app_src)

    config = QTWSConfig(app_src)

    script_path = HOME_PATH + "/" + "main.py -a " + os.path.basename(app_src).replace(".qtws", "")

    content = "[Desktop Entry]\n" \
              "Categories=Internet\n" \
              "Comment=" + config.name + "\n" \
              "Exec=" + script_path + "\n" \
              "GenericName=" + config.name + "\n" \
              "Icon=" + HOME_PATH + "/" + config.icon + "\n" \
              "MimeType=\n" \
              "Name=" + config.name + "\n" \
              "Path=\n" \
              "StartupNotify=true\n" \
              "Terminal=false\n" \
              "Type=Application"
    with open(desktop_dest, "w") as f:
        f.write(content)


if sys.platform not in SUPPORTED_OS:
    print("ERROR: Your operating system is not supported yet.")

for app in glob.glob("apps/*.qtws"):
    app_base_name = app.replace("apps/", "").replace(".qtws", "")
    desktop_file = os.path.join(HOME_PATH, "desktops/" + app_base_name + ".desktop")
    make_desktop_file(app, desktop_file)

    if sys.platform == "linux":
        system_app = "/usr/share/applications/qtws-app-" + app_base_name  + ".desktop"
        if os.path.exists(system_app):
            os.remove(system_app)

        os.symlink(desktop_file, system_app)

setuptools.setup(name='pyqtws',
                 version='0.1',
                 description='Standalone website wrapper',
                 url='http://github.com/intersimone999/pyqtws',
                 author='Simone Scalabrino',
                 author_email='simone@datasound.it',
                 license='MIT',
                 packages=["pyqtws"],
                 install_requires=[
                     'PyQt5', 'PyQtWebEngine', 'dbus-python', 'pygi'
                 ],
                 zip_safe=False)
