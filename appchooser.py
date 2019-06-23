import os
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from threading import Thread

class AppChooser:
    def __init__(self, servingDirectory, port=9000):
        self.servingDirectory = servingDirectory
        self.port = port
        
    def startServing(self):
        os.chdir(self.servingDirectory)
        TCPServer.allow_reuse_address = True
        self.server = TCPServer(("", self.port), SimpleHTTPRequestHandler)
        self.thread = Thread(target=self.__serve)
        self.thread.start()
        
    def __serve(self):
        print("Started serving on " + str(self.port))
        self.server.serve_forever()
        print("Done")
        
    def stopServing(self):
        self.server.shutdown()
