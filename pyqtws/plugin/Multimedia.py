from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWidgets import QAction, QMenu

from silo_window import QTWSMainWindow
from plugins import QTWSPlugin
from web import QTWSWebView
from config import QTWSConfig

from threading import Thread
from dbus.service import Object
import main

import logging
import random
import time
import dbus
import dbus.mainloop.glib


class Multimedia(QTWSPlugin):
    def __init__(self, config: QTWSConfig):
        super().__init__("Multimedia")
        self.web = None
        self.window = None
        self.audio_toggle = None
        self.play_pause_action = None
        self.config = config
        self.__mpris2 = None
        self.terminated = False

    def window_setup(self, window: QTWSMainWindow):
        self.window = window
        if self.web:
            self.__init_mpris2()

    def web_engine_setup(self, web: QTWSWebView):
        self.web = web
        if self.window:
            self.__init_mpris2()

    def on_page_loaded(self, url: QUrl):
        if self.__mpris2:
            self.__check_completed(False)

    def __check_completed(self, completed):
        if not completed and not self.terminated:
            self.web.page().runJavaScript("document.readyState === \"complete\"", self.__check_completed)
        else:
            self.__mpris2.refresh_properties()

    def add_menu_items(self, menu: QMenu):
        self.audio_toggle = None
        if self.web.page().isAudioMuted():
            self.audio_toggle = QAction(QIcon.fromTheme("audio-volume-muted"), "Unmute")
        else:
            self.audio_toggle = QAction(QIcon.fromTheme("audio-volume-high"), "Mute")

        self.audio_toggle.triggered.connect(lambda: self.web.page().setAudioMuted(not self.web.page().isAudioMuted()))
        menu.addAction(self.audio_toggle)

        if self.__mpris2.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus") == "Playing":
            self.play_pause_action = QAction(QIcon.fromTheme("media-playback-pause"), "Pause")
            self.play_pause_action.triggered.connect(self.__mpris2.Pause)
        else:
            self.play_pause_action = QAction(QIcon.fromTheme("media-playback-start"), "Play")
            self.play_pause_action.triggered.connect(self.__mpris2.Play)

        menu.addAction(self.play_pause_action)
        
    def close_event(self, window: QTWSMainWindow, event: QCloseEvent):
        self.terminated = True

    def __init_mpris2(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        self.__mpris2 = MultimediaPluginMPRIS2(self.config.app_id, self.config.name, self.window, self.web)

        self.__metadata = dict()
        self.__web_thread = Thread(target=self.__update_playback_status)
        self.__web_thread.start()

    def __update_playback_status(self):
        time.sleep(5)
        while self.window.isVisible():
            time.sleep(1)
            self.__mpris2.refresh_properties()
            
            if self.web.page().title():
                self.__metadata["xesam:album"] = self.config.name
                self.__metadata["xesam:title"] = self.web.page().title()
                self.__metadata["xesam:url"] = self.web.page().url().toString()
                
                self.__mpris2.set_metadata(self.__metadata)

class MultimediaPluginMPRIS2(Object):
    MPRIS_INTERFACE = "org.mpris.MediaPlayer2"
    MPRIS_PLAYER_INTERFACE = "org.mpris.MediaPlayer2.Player"

    def __init__(self, app_id: str, name: str, window: QTWSMainWindow, web: QTWSWebView):
        global qtws_app_id
        self.bus = dbus.SessionBus()
        self.service_name = "org.mpris.MediaPlayer2.qtws_" + name + str(random.randint(0, 9999))
        bus_name = dbus.service.BusName(self.service_name, bus=self.bus)

        super().__init__(bus_name, "/org/mpris/MediaPlayer2")
        self.window = window
        self.web = web

        self.track_path = "/it/datasound/mpris/" + str(random.randint(0, 9999))
        self.track = Object(bus_name, self.track_path)

        self.properties = dict()
        self.properties[self.MPRIS_INTERFACE] = dict()
        self.properties[self.MPRIS_INTERFACE]["CanQuit"] = True
        self.properties[self.MPRIS_INTERFACE]["CanRaise"] = False
        self.properties[self.MPRIS_INTERFACE]["HasTrackList"] = False
        self.properties[self.MPRIS_INTERFACE]["Identity"] = name

        self.properties[self.MPRIS_INTERFACE]["DesktopEntry"] = "silos-" + app_id
        self.properties[self.MPRIS_INTERFACE]["SupportedUriSchemes"] = dbus.Array([], signature="s")
        self.properties[self.MPRIS_INTERFACE]["SupportedMimeTypes"] = dbus.Array([], signature="s")
        self.PropertiesChanged(self.MPRIS_INTERFACE, self.properties[self.MPRIS_INTERFACE], [])

        self.properties[self.MPRIS_PLAYER_INTERFACE] = dict()
        self.properties[self.MPRIS_PLAYER_INTERFACE]["PlaybackStatus"] = "Stopped"
        self.properties[self.MPRIS_PLAYER_INTERFACE]["LoopStatus"] = "None"
        self.properties[self.MPRIS_PLAYER_INTERFACE]["Shuffle"] = False
        self.properties[self.MPRIS_PLAYER_INTERFACE]["Volume"] = 1.0
        self.properties[self.MPRIS_PLAYER_INTERFACE]["Rate"] = 1.0
        self.properties[self.MPRIS_PLAYER_INTERFACE]["MinimumRate"] = 0.01
        self.properties[self.MPRIS_PLAYER_INTERFACE]["MaximumRate"] = 32.0
        self.properties[self.MPRIS_PLAYER_INTERFACE]["Position"] = 0
        self.properties[self.MPRIS_PLAYER_INTERFACE]["CanGoNext"] = False
        self.properties[self.MPRIS_PLAYER_INTERFACE]["CanGoPrevious"] = False
        self.properties[self.MPRIS_PLAYER_INTERFACE]["CanPlay"] = True
        self.properties[self.MPRIS_PLAYER_INTERFACE]["CanPause"] = True
        self.properties[self.MPRIS_PLAYER_INTERFACE]["CanSeek"] = True
        self.properties[self.MPRIS_PLAYER_INTERFACE]["CanControl"] = True
        self.PropertiesChanged(self.MPRIS_PLAYER_INTERFACE, self.properties[self.MPRIS_PLAYER_INTERFACE], [])

    @dbus.service.method(MPRIS_INTERFACE, in_signature='', out_signature='')
    def Raise(self):
        """
        MPRIS method not implemented yet
        """
        pass

    @dbus.service.method(MPRIS_INTERFACE, in_signature='', out_signature='')
    def Quit(self):
        self.window.close()

    @dbus.service.method(MPRIS_PLAYER_INTERFACE, in_signature='', out_signature='')
    def Pause(self):
        js = "document.getElementsByTagName(\"video\")[0].pause()"
        self.web.page().runJavaScript(js)
        self.refresh_properties()

    @dbus.service.method(MPRIS_PLAYER_INTERFACE, in_signature='', out_signature='')
    def Play(self):
        js = "document.getElementsByTagName(\"video\")[0].play()"
        self.web.page().runJavaScript(js)
        self.refresh_properties()

    @dbus.service.method(MPRIS_PLAYER_INTERFACE, in_signature='', out_signature='')
    def PlayPause(self):
        js = "x=document.getElementsByTagName(\"video\"); if (x[0].paused) {x[0].play()} else {x[0].pause()}; "
        self.web.page().runJavaScript(js)
        self.refresh_properties()

    @dbus.service.method(MPRIS_PLAYER_INTERFACE, in_signature='x', out_signature='')
    def Seek(self, time_in_microseconds):
        time_in_seconds = time_in_microseconds / (1000 * 1000)
        js = "document.getElementsByTagName(\"video\")[0].currentTime += " + str(time_in_seconds)
        self.web.page().runJavaScript(js)
        self.refresh_properties()

    @dbus.service.method(MPRIS_PLAYER_INTERFACE, in_signature='', out_signature='')
    def Next(self):
        """
        MPRIS method not implemented yet
        """
        pass

    @dbus.service.method(MPRIS_PLAYER_INTERFACE, in_signature='', out_signature='')
    def Previous(self):
        """
        MPRIS method not implemented yet
        """
        pass

    @dbus.service.method(MPRIS_PLAYER_INTERFACE, in_signature='', out_signature='')
    def Stop(self):
        """
        MPRIS method not implemented yet
        """
        pass

    @dbus.service.method(MPRIS_PLAYER_INTERFACE, in_signature='x', out_signature='')
    def Stop(self, x):
        """
        MPRIS method not implemented yet
        """
        pass

    @dbus.service.method(MPRIS_PLAYER_INTERFACE, in_signature='ox', out_signature='')
    def SetPosition(self, o, time_in_microseconds):
        time_in_seconds = time_in_microseconds / (1000 * 1000)
        js = "document.getElementsByTagName(\"video\")[0].currentTime = " + str(time_in_seconds)
        self.web.page().runJavaScript(js)
        self.refresh_properties()

    @dbus.service.method(MPRIS_PLAYER_INTERFACE, in_signature='s', out_signature='')
    def OpenUri(self, s):
        """
        MPRIS method not implemented yet
        """
        pass

    @dbus.service.method("org.freedesktop.DBus.Properties", in_signature='ss', out_signature='v')
    def Get(self, interface_name, key):
        value = self.properties[interface_name][key]
        if type(value) == dict:
            value = dbus.Dictionary(value, signature="sv")

        return value

    @dbus.service.method("org.freedesktop.DBus.Properties", in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface_name):
        result = dbus.Dictionary(self.properties[interface_name], signature="sv")

        for key in self.properties[interface_name].keys():
            if type(self.properties[interface_name][key]) == dict:
                result[key] = dbus.Dictionary(self.properties[interface_name][key], signature="sv")

        return result

    @dbus.service.method("org.freedesktop.DBus.Properties", in_signature='ssv', out_signature='')
    def Set(self, interface_name, key, value):
        if interface_name in self.properties.keys() and key in self.properties[interface_name].keys():
            changed = self.properties[interface_name][key] != value
        else:
            changed = True

        self.properties[interface_name][key] = value
        properties_changed = dict()

        properties_changed[key] = value
        if changed and key != "Position":
            self.PropertiesChanged(interface_name, properties_changed, [])

    @dbus.service.signal("org.freedesktop.DBus.Properties", signature='sa{sv}as')
    def PropertiesChanged(self, interface_name, changed_properties, invalidated_properties):
        """
        MPRIS method not implemented yet
        """
        pass
    
    def set_metadata(self, metadata):
        if metadata:
            metadata["mpris:trackid"] = dbus.ObjectPath(self.track_path)
            self.Set(self.MPRIS_PLAYER_INTERFACE, "Metadata", dbus.Dictionary(metadata, signature="sv"))
        else:
            self.properties[self.MPRIS_PLAYER_INTERFACE].pop("Metadata")
            self.PropertiesChanged(self.MPRIS_PLAYER_INTERFACE, None, ["Metadata"])

    def refresh_properties(self):
        js_for_has_player = "document.getElementsByTagName(\"video\").length > 0 && " \
                            "document.getElementsByTagName(\"video\")[0].src.length > 0 "
        self.web.page().runJavaScript(js_for_has_player, self.__set_has_player)

        if self.MPRIS_PLAYER_INTERFACE in self.properties.keys() and \
                "Volume" in self.properties[self.MPRIS_PLAYER_INTERFACE].keys():
            volume_level = str(self.properties[self.MPRIS_PLAYER_INTERFACE]["Volume"])
            js_for_volume = "document.getElementsByTagName(\"video\")[0].volume = " + volume_level
            self.web.page().runJavaScript(js_for_volume)

    def __set_has_player(self, has_player):
        if has_player:
            js_for_playing = "document.getElementsByTagName(\"video\")[0].paused == false"
            self.web.page().runJavaScript(js_for_playing, self.__set_is_playing)

            js_for_position = "document.getElementsByTagName(\"video\")[0].getCurrentTime()"
            self.web.page().runJavaScript(js_for_position, self.__set_position)

            js_for_rate = "document.getElementsByTagName(\"video\")[0].playbackRate"
            self.web.page().runJavaScript(js_for_rate, self.__set_rate)

            js_for_length = "document.getElementsByTagName(\"video\")[0].getDuration()"
            self.web.page().runJavaScript(js_for_length, self.__set_metadata_length)
        else:
            self.Set(self.MPRIS_PLAYER_INTERFACE, "PlaybackStatus", "Stopped")
            self.__set_position(0)
            self.__set_rate(1.0)
            self.__set_metadata_length(0.0)

    def __set_is_playing(self, is_playing):
        if is_playing:
            self.Set(self.MPRIS_PLAYER_INTERFACE, "PlaybackStatus", "Playing")
        else:
            self.Set(self.MPRIS_PLAYER_INTERFACE, "PlaybackStatus", "Paused")

    def __set_position(self, position):
        if position:
            self.Set(self.MPRIS_PLAYER_INTERFACE, "Position", dbus.Int64(position * 1000 * 1000))
            
        logging.debug(self.properties[self.MPRIS_PLAYER_INTERFACE]["Position"])

    def __set_rate(self, rate):
        if rate:
            self.Set(self.MPRIS_PLAYER_INTERFACE, "Rate", dbus.Double(rate))

    def __set_metadata_length(self, length):
        if length and "Metadata" in self.properties[self.MPRIS_PLAYER_INTERFACE]:
            length = length * 1000 * 1000
            self.properties[self.MPRIS_PLAYER_INTERFACE]["Metadata"]["mpris:length"] = dbus.Int64(length)
            metadata = self.properties[self.MPRIS_PLAYER_INTERFACE]["Metadata"]
            changed = dict()
            changed["Metadata"] = dbus.Dictionary(metadata, signature="sv")
            self.PropertiesChanged(self.MPRIS_PLAYER_INTERFACE, changed, [])


def instance(config: QTWSConfig, params: dict):
    return Multimedia(config)
