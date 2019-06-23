from plugins import QTWSPlugin

class GoogleAuthentication(QTWSPlugin):
    def __init__(self):
        super().__init__("GoogleAuthentication")
        
    def isURLWhitelisted(self, url):
        # Check google authentication URL
        return False
    
def instance(params):
    return GoogleAuthentication()
