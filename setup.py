#!/usr/bin/env python

import setuptools
import os
import glob

setuptools.setup(name='pyqtws',
                 version='0.1.51',
                 scripts=["silo"],
                 description='Standalone website wrapper',
                 url='http://github.com/intersimone999/pyqtws',
                 author='Simone Scalabrino',
                 author_email='simone@datasound.it',
                 license='MIT',
                 packages=setuptools.find_packages(),
                 install_requires=[
                     'PyQt5', 'PyQtWebEngine', 'dbus-python', 'pygi', 'pystray'
                 ],
                 zip_safe=False)
