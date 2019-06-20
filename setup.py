from setuptools import setup

setup(name='pyqtws',
      version='0.1',
      description='Standalone site wrapper',
      url='http://github.com/intersimone999/pyqtws',
      author='Simone Scalabrino',
      author_email='simone@datasound.it',
      license='MIT',
      packages=['funniest'],
      install_requires=[
          'PyQt5==5.12.1', 'PyQtWebEngine==5.12.1'
      ],
      zip_safe=False)
