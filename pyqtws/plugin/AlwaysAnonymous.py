from config import QTWSConfig
from plugins import QTWSPlugin

import webbrowser
import hashlib


class AlwaysAnonymous(QTWSPlugin):    
    def __init__(self, config):
        super().__init__("AlwaysAnonymous")
        self.config = config
        self.profile_manager = None
    
    def web_profile_candidate(self, candidates: list):
        candidates.clear()
        candidates.append("")

def instance(config: QTWSConfig, params: dict):
    return AlwaysAnonymous(config)
