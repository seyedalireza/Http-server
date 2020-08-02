import threading
import socket as sc


class HttpProxyServer(threading.Thread):

    def __init__(self, port):
        super().__init__()
        self.name = "HttpProxyServer-" + str(port)
        self.port: int = port
        self.socket: sc.socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
        self.connections = list()
        self.is_running = False
        # TODO start another socket for statistic queries

    def run(self) -> None:
        """
        This function runs a simple http server.
        """
        self.is_running = True
        socket = self.socket
        socket.bind(("localhost", self.port))
        print("Http proxy server started on port " + str(self.port))

        # Listen for incoming connections
        socket.listen(1)

        while self.is_running:
            connection, address = socket.accept()
            print("proxy-Connection established from " + str(address))
