#!/usr/bin/env python

import setuptools
import os
import glob

from pyqtws.config import QTWSConfig

SRCDIR = "pyqtws"
HOME_PATH = os.path.dirname(os.path.realpath(__file__)) + "/" + SRCDIR


def make_desktop_file(app_src, desktop_dest):
    print("Building desktop file for " + app_src)

    config = QTWSConfig(app_src)

    script_path = "silo -a " + os.path.basename(app_src).replace(".qtws", "")

    content = "[Desktop Entry]\n" \
              "Categories=Internet\n" \
              "Comment=" + config.description + "\n" \
              "Exec=" + script_path + "\n" \
              "GenericName=" + config.name + "\n" \
              "Icon=" + config.icon + "\n" \
              "MimeType=\n" \
              "Name=" + config.name + "\n" \
              "Path=\n" \
              "StartupNotify=true\n" \
              "Terminal=false\n" \
              "Type=Application"
    with open(desktop_dest, "w") as f:
        f.write(content)


for app in glob.glob("pyqtws/apps/*.qtws"):
    app_base_name = app.replace("pyqtws/apps/", "").replace(".qtws", "")
    desktop_file = os.path.join(HOME_PATH, "desktops/" + app_base_name + ".desktop")
    make_desktop_file(app, desktop_file)


package_data = {
    "pyqtws.apps": list(map(lambda f: os.path.basename(f), glob.glob(SRCDIR + "/apps/*.qtws"))),
    "pyqtws.apps.appChooser": list(map(lambda f: os.path.basename(f), glob.glob(SRCDIR + "/apps/appChooser*.qtws"))),
    "pyqtws.icons": list(map(lambda f: os.path.basename(f), glob.glob(SRCDIR + "/icons/*"))),
    "pyqtws.desktops": list(map(lambda f: os.path.basename(f), glob.glob(SRCDIR + "/desktops/*")))
}

setuptools.setup(name='silo',
                 version='0.1',
                 scripts=["silo"],
                 description='Standalone website wrapper',
                 url='http://github.com/intersimone999/pyqtws',
                 author='Simone Scalabrino',
                 author_email='simone@datasound.it',
                 license='MIT',
                 packages=setuptools.find_packages(),
                 install_requires=[
                     'PyQt5', 'PyQtWebEngine', 'dbus-python', 'pygi'
                 ],
                 package_data=package_data,
                 zip_safe=False)
