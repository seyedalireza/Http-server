import threading
import time
import socket as sc
from wsgiref.handlers import format_date_time
import ResponseCreator
import HP


class HttpServer(threading.Thread):

    def __init__(self, port):
        super().__init__()
        self.name = "HttpServer-" + str(port)
        self.port: int = port
        self.socket: sc.socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
        self.connections = list()
        self.is_running = False

    def run(self) -> None:
        """
        This function runs a simple http server.
        """
        self.is_running = True
        socket = self.socket
        socket.bind(("localhost", self.port))
        print("Http server started on port " + str(self.port))

        # Listen for incoming connections
        socket.listen(1)

        while self.is_running:
            connection, address = socket.accept()
            print("Connection established from " + str(address))
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
        self.connection: sc.socket = connection
        self.client_add = client_address
        self.connection.settimeout(HP.TIME_OUT)
        self.alive_time = time.time() + 60
        super().__init__()
        self.is_running = False

    def run(self) -> None:
        """
        Implementation of request handler.
        """
        self.is_running = True
        while time.time() <= self.alive_time and self.is_running:
            input_data = bytearray()
            while True:
                try:
                    self.connection.settimeout(self.alive_time - time.time())
                    data = self.connection.recv(2048)
                    input_data.extend(data)
                    if not data or (b"\r\n" in input_data):
                        break
                except:
                    self.connection.close()
                    return
            data, keep_alive = ResponseCreator.response_creator(input_data.decode())
            self.connection.send(data.to_byte())
            print("[" + format_date_time(time.time()) + "]\t" + input_data.decode().splitlines()[0] + "\t" +
                  data.header_str().splitlines()[0])
            if keep_alive:
                self.alive_time = time.time() + keep_alive
            else:
                self.connection.close()
                return
        try:
            self.connection.close()
        except:
            pass
        self.is_running = False

    def stop(self):
        self.is_running = False
        try:
            self.connection.close()
        except:
            pass
