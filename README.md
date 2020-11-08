[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=intersimone999_pyqtws&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=intersimone999_pyqtws)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=intersimone999_pyqtws&metric=vulnerabilities)](https://sonarcloud.io/dashboard?id=intersimone999_pyqtws)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=intersimone999_pyqtws&metric=bugs)](https://sonarcloud.io/dashboard?id=intersimone999_pyqtws)
# Silos
A python re-implementation of QTWS.

Silos is a QT webengine program to easily create very basic and lightweight desktop webapps. Silos integrates a set of pre-defined apps. Make a pull request at https://github.com/intersimone999/silos-apps to integrate more apps.

## Requirements
- qt5
- qtwebegine (with proprietary codecs, needed for some webapps like Netflix, but not for all of them)

Arch users do not need to compile qtwebengine with proprietary codecs, the offical package has them enabled.

Ubuntu 17.04/17.10 - qtwebengine comes with proprietary codecs

       Grab the deb package from releases
       chmod +x widevine.sh
       sudo ./widevine.sh

Most others must compile qtwebengine with proprietary codecs.

Read this <html>http://blog.qt.io/blog/2016/06/03/netflix-qt-webengine-5-7/</html>

## Installation
- Run `python setup.py bdist_wheel`
- Run `pip install dist/*.whl`

## Run
To run a silo, you can run the shell script `silo`, specifying:

- The name of the app that you want to run. The app must be in the `pyqtws/apps` folder and its name must be in lowercase;
- The URL that you want to open; in that case, the script will open the URL with the most suited app or the default web browser, based on its scope.

Examples:
- To open Netflix, run `python main.py -a Netflix` or `python main.py --app Netflix`
- To open a YouTube video with a given URL, run `python main.py "https://www.youtube.com/watch?v=2MpUj-Aua48"`

## Features
Silos allows you to easily create an embedded version of an online webapp. 
A silo features a context menu that can be activated with a right click anywhere. This menu allows to go back, to go to the home of the webapp and to reload the page.

Each app is completely isolated from the others: it will have its own cache, cookies and storage.

To run a silo, it is necessary to specify a configuration file which gives instructions about the webapp that needs to be run. This is an example for YouTube:

```json
{
        "name": "YouTube",
        "home": "http://youtube.com",
        "icon": "youtube-desktop.svg",
        "saveSession": false,
        
        "plugins": [{"name": "Multimedia"}],
        "scope": ["https?:\/\/.*\.youtube\.com(?:\/.*|)"],
        
        "menu": [
            {
                "title": "Trending",
                "action": "http://youtube.com/feed/trending"
            },
            {
                "title": "Subscriptions",
                "action": "http://youtube.com/feed/subscriptions"
            },
            {
                "title": "History",
                "action": "http://youtube.com/feed/history"
            },
            {
                "title": "Playlist",
                "action": "http://youtube.com/playlist"
            },
            {
                "title": "Trending",
                "action": "http://youtube.com/feed/trending"
            },
            {
                "title": "Settings",
                "action": "http://youtube.com/account"
            }
        ]
}
```

The fields of the json are the following (required in italics):
- *name*: name of the webapp (string);
- *home*: URL of the homepage of the webapp (string);
- *icon*: local path of the icon that the application should show (string);
- *saveSession*: if the session has to be saved when the window is closed (e.g., the last page visited) (boolean);
- *plugins*: list of the plugins needed (array of strings JSON objects with the fields "name" (required string) and "params" (optional array of strings));
- *scope*: regular expressions of the domains that are allowed in the webapp. URLs belonging to domains not matching with any of the scopes will be openend with the browser (array of strings);
- menu: additional entries in the contextual menu (array of objects with a title, indicating the name of the menu entry, and an action, indicating the URL that will be set if the entry is selected).
- alwaysOnTop: sets the app always on top.
- cacheMB: maximum size of the cache (in MB). Default is 50.

## Plugin
Silos is easily extensible through plugin. A plugin must be placed in the `plugin` directory. The name of the plugin must match the name of the file and the name of the class. Each plugin script must have a `instantiate` method that returns the instance of the plugin. Check the `Multimedia` plugin to see an example.

Plugins allow to make some actions when some events happen. To see the full list of available actions, see the class `QTWSPlugin` in `plugins.py`.

## License
The following icons are from [icons8](https://icons8.com/):

- Amazon
- Amazon Prime Video
- Google Drive
- Google Maps
- Google Photos
- Google Sheets
- Netflix
- Office365
- Twitch
- WhatsApp
- YouTube

The icon for "hey.com" is from the official website..
All the apps included in the basic installation are **unofficial**.

## Troubleshooting 
If you receiving an error for Netflix or similar webapps, you need to install widevine (e.g., the AUR chromium-widevine in Arch Linux).
