from plugins import QTWSPlugin
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction

class Multimedia(QTWSPlugin):
    def __init__(self):
        super().__init__("Multimedia")
        
    def webEngineSetup(self, web):
        self.web = web
    
    def addMenuItems(self, menu):
        self.audioToggle = None
        if self.web.page().isAudioMuted():
            self.audioToggle = QAction(QIcon.fromTheme("audio-volume-muted"), "Unmute")
        else:
            self.audioToggle = QAction(QIcon.fromTheme("audio-volume-high"), "Mute")
            
        self.audioToggle.triggered.connect(lambda: self.web.page().setAudioMuted(not self.web.page().isAudioMuted()))
        menu.addAction(self.audioToggle)
        
        self.playPauseAction = QAction(QIcon.fromTheme("media-playback-start"), "Play/Pause")
        self.playPauseAction.triggered.connect(lambda: self.web.page().runJavaScript("x=document.getElementsByTagName(\"video\"); for(i = 0; i < x.length; i++) {if (x[i].paused) {x[i].play()} else {x[i].pause()}};"))
        
        menu.addAction(self.playPauseAction)
    
def instance(params):
    return Multimedia()
