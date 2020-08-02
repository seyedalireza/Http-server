import threading
import socket as sc
import time


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
        This function runs a simple http proxy server.
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
            request_handler = RequestHandler(connection, address)
            self.connections.append(request_handler)
            request_handler.start()

    def stop(self) -> None:
        """
        Stop Http server and close connections.
        """
        self.socket.close()
        self.is_running = False
        for rh in self.connections:
            if rh.is_running:
                rh.stop()


class RequestHandler(threading.Thread):

    def __init__(self, connection, client_address):
        """
        This constructor should always be called with keyword arguments. Arguments are:

        :param connection: socket representing the connection
        :param client_address: the address info is a pair (host address, port)
        """
        super().__init__()
        self.connection: sc.socket = connection
        self.target_connection = None
        self.client_address = client_address
        self.connection.settimeout(60)
        self.alive_time = time.time() + 60
        self.is_running = False

    def run(self) -> None:
        """
        Implementation of request handler.
        """
        self.is_running = True
        while time.time() <= self.alive_time and self.is_running:
            query = self.read_until_new_line()
            print(query.decode())
            # TODO: parse request and convert it to another query and open connection of it is closed.
            # TODO: handle if query has body (content-length)
        self.connection.close()
        self.is_running = False

    def read_until_new_line(self):
        input_data = bytearray()
        while True:
            try:
                self.connection.settimeout(self.alive_time - time.time())
                data = self.connection.recv(2048)
                print(data.decode())
                input_data.extend(data)
                if not data or data.decode().splitlines()[-1] == "":
                    break
            except:
                self.connection.close()
                return -1
        return input_data

    def stop(self):
        self.is_running = False
