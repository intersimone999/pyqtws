import os
import glob
import platform
from pathlib import Path

class QTWSFolderManager:
    HOME = None
    
    def setup(paths=None):
        QTWSFolderManager.HOME = None
        __user_home = str(Path.home())
        
        if paths is None:
            paths = []
            
            if platform.system().lower() == 'linux':
                paths.append("/usr/share/silos-apps")
            
            paths.append(os.path.join(__user_home, ".local", "share", "silos-apps"))
            paths.append(os.path.dirname(os.path.realpath(__file__)))
        
        while QTWSFolderManager.HOME is None and len(paths) > 0:
            candidate = paths.pop(0)
            if os.path.exists(candidate):
                QTWSFolderManager.HOME = candidate
        
        if QTWSFolderManager.HOME is None:
            raise NoHomeFolderError()
    
    def home_folder():
        return os.path.join(QTWSFolderManager.HOME)
    
    def apps_folder():
        return os.path.join(QTWSFolderManager.HOME, "apps")
    
    def all_apps():
        return glob.iglob(os.path.join(QTWSFolderManager.apps_folder(), "*.qtws"))
    
    def app_file(name):
        if not name.endswith(".qtws"):
            name = name + ".qtws"
        
        return os.path.join(QTWSFolderManager.apps_folder(), name)
    
    def icons_folder():
        return os.path.join(QTWSFolderManager.HOME, "icons") 
    
    def icon_path(icon):
        return os.path.join(QTWSFolderManager.HOME, icon)


class NoHomeFolderError(Exception):
    pass
