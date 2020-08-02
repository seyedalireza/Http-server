import threading
import socket as sc
import time
from ProxyUtils import *


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


def split_url(url: str):
    if url.lower().startswith("http://"):
        spited = url.split("/")
        return spited[2], "/" + "/".join(spited[3:])
    else:
        spited = url.split("/")
        return spited[0], "/" + "/".join(spited[1:])


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
            query = self.read_until_new_line(self.connection)
            if query == -1:
                break
            query = HTTP_request_parser(query.decode())
            url, path = split_url(query.URL)
            if self.target_connection is None:
                self.target_connection = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
                self.target_connection.connect((sc.gethostbyname(url), 80))
            server_message = HTTPRequest.create_server_request(query, path)
            try:
                self.target_connection.send(server_message.to_byte())
            except:
                break
            response = self.read_response()
            if response == -1:
                break
            try:
                self.connection.send(response)
            except:
                break
            print(query.decode())
            # TODO: parse request and convert it to another query and open connection of it is closed.
            # TODO: handle if query has body (content-length)
        try:
            self.connection.close()
        except:
            pass
        try:
            self.target_connection.close()
        except:
            pass
        self.is_running = False

    def read_response(self):
        headers = self.read_until_new_line(self.target_connection)
        if headers == -1:
            return -1
        headers_lines = headers.decode().split("\r\n")[1:]
        is_chunk = False
        content_len = 0
        for line in headers_lines:
            spited = line.split(": ")
            if spited[0] == "Content-Length":
                content_len = int(spited[1])
            elif spited[0] == "Transfer-Encoding" and spited[1] == "chunked":
                is_chunk = True
        body = self.read_body(content_len, self.target_connection, is_chunk)
        if body == -1:
            return -1
        return headers.extend(body)

    def read_until_new_line(self, connection):
        input_data = bytearray()
        while True:
            try:
                connection.settimeout(self.alive_time - time.time())
                data = connection.recv(2048)
                print(data.decode())
                input_data.extend(data)
                if not data or data.decode().splitlines()[-1] == "":
                    break
            except:
                connection.close()
                return -1
        return input_data

    def read_body(self, length, socket, is_chunk: bool):
        input_data = bytearray()
        while is_chunk or len(input_data) < length:
            try:
                socket.settimeout(self.alive_time - time.time())
                data = socket.recv(2048)
                if is_chunk and len(data) == 0:
                    break
                input_data.extend(data)
            except:
                socket.close()
                return -1
        return input_data

    def stop(self):
        self.is_running = False

