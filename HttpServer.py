import threading
import time
import socket as sc
import ResponseCreator
import logging
import HP

class HttpServer(threading.Thread):

    def __init__(self, port):
        super().__init__()
        self.name = "HttpServer-" + str(port)
        self.port: int = port
        self.socket: sc.socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
        self.open_connections = list()

    def run(self) -> None:
        """
        This function runs a simple http server.
        """
        socket = self.socket
        socket.bind(("localhost", self.port))
        print("Http server started on port " + str(self.port))

        # Listen for incoming connections
        socket.listen(1)

        while True:
            connection, address = socket.accept()
            print("Connection established from " + str(address))
            request_handler = RequestHandler(connection, address)
            self.open_connections.append(request_handler)
            request_handler.start()

        # TODO close connection


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

    def run(self) -> None:
        """
        Implementation of request handler.
        """
        while time.time() <= self.alive_time:
            input_data = bytearray()
            while True:
                try:
                    data = self.connection.recv(2048)
                    print(data.decode())
                    if not data or data.decode() == "\r\n":
                        break
                    input_data.extend(data)
                except IOError:
                    self.connection.close()
                    return
            print(input_data.decode())
            data, keep_alive = ResponseCreator.response_creator(input_data.decode())
            self.connection.send(data.to_byte())
            if keep_alive:
                self.alive_time = time.time() + keep_alive
            else:
                self.connection.close()
                return
        self.connection.close()
