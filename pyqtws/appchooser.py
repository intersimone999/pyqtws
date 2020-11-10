import os
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from threading import Thread


class AppChooser:
    def __init__(self, serving_directory: str, port: int = 9000):
        self.serving_directory = serving_directory
        self.port = port
        self.server = None
        self.thread = None

    def start_serving(self):
        os.chdir(self.serving_directory)
        TCPServer.allow_reuse_address = True
        self.server = TCPServer(("", self.port), SimpleHTTPRequestHandler)
        self.thread = Thread(target=self.__serve)
        self.thread.start()

    def __serve(self):
        print("Started serving on " + str(self.port))
        self.server.serve_forever()
        print("Done")

    def stop_serving(self):
        self.server.shutdown()
