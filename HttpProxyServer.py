import socket as sc
import threading
import time
from dns import resolver
from dns import reversename

from ProxyUtils import *


class ProxyAnalyzer(threading.Thread):
    client_packet_lengths = []
    server_packet_lengths = []
    server_body_lengths = []
    type_count = dict({})
    status_count = dict({})
    visits = dict({})

    def __init__(self, port):
        super().__init__()
        self.port: int = port
        self.socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
        self.connections = list()
        self.is_running = False

    def run(self) -> None:
        self.is_running = True
        socket = self.socket
        socket.bind(("localhost", self.port))
        socket.listen(1)
        while self.is_running:
            connection, address = socket.accept()
            analyze_handler = AnalyzerHandler(connection, address)
            self.connections.append(analyze_handler)
            analyze_handler.start()

    def stop(self) -> None:
        try:
            self.socket.close()
        except:
            pass
        self.is_running = False
        for rh in self.connections:
            if rh.is_running:
                rh.stop()

    def handle_client_packet(self, pkt: bytearray):
        self.client_packet_lengths.append(len(pkt))
        print("Client: " + str(self.client_packet_lengths))

    def handle_server_packet(self, http_response: HTTPProxyResponse):
        self.server_packet_lengths.append(len(http_response.to_byte()))
        self.server_body_lengths.append(len(http_response.body))
        tmp_str = http_response.status_code + " " + http_response.status_msg
        if not self.status_count.__contains__(tmp_str):
            self.status_count[tmp_str] = 0
        self.status_count[tmp_str] += 1
        if http_response.headers.__contains__("Content-Type"):
            tmp_type = http_response.headers["Content-Type"].split(", ")
            for t in tmp_type:
                t = t.split("; ")[0]
                if not self.type_count.__contains__(t):
                    self.type_count[t] = 0
                self.type_count[t] += 1
        print("Server:")
        print(self.server_packet_lengths)
        print(self.server_body_lengths)
        print(self.type_count)
        print(self.status_count)

    def add_visitor(self, url: str):
        if not self.visits.__contains__(url):
            self.visits[url] = 0
        self.visits[url] += 1
        print("Visited:")
        print(self.visits)


def represent_int(param):
    try:
        int(param)
        return True
    except ValueError:
        return False


class AnalyzerHandler(threading.Thread):

    def __init__(self, connection, client_address):
        super().__init__()
        self.connection: sc.socket = connection
        self.client_address = client_address
        self.is_running = False

    def run(self) -> None:
        self.is_running = True
        while self.is_running:
            try:
                request = self.connection.recv(2048).decode()
            except:
                break
            if request == "packet length stats":
                # TODO
                pass
            elif request == "type count":
                # TODO
                pass
            elif request == "status count":
                # TODO
                pass
            elif request[:4] == "top " and request[-14:] == " visited hosts" and represent_int(request[4:-14]):
                # TODO
                pass
            else:
                # TODO
                pass
        try:
            self.connection.close()
        except:
            pass

    def stop(self):
        self.is_running = False


class HttpProxyServer(threading.Thread):

    def __init__(self, port, analyzer: ProxyAnalyzer):
        super().__init__()
        self.name = "HttpProxyServer-" + str(port)
        self.port: int = port
        self.socket: sc.socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
        self.connections = list()
        self.is_running = False
        self.analyzer = analyzer
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
            request_handler = RequestHandler(connection, address, self.analyzer)
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

    def __init__(self, connection, client_address, analyzer: ProxyAnalyzer):
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
        self.analyzer = analyzer

    def run(self) -> None:
        """
        Implementation of request handler.
        """
        self.is_running = True
        while time.time() <= self.alive_time and self.is_running:
            query, _ = self.read_chunck(self.connection)
            if query == -1 or query is None or len(query) == 0:
                break
            self.analyzer.handle_client_packet(query)
            query = HTTP_request_parser(query.decode())
            if query.headers.__contains__("Keep-Alive"):
                self.alive_time = time.time() + query.headers["Keep-Alive"]
            if query.headers.__contains__("Connection") and query.headers["Connection"] == "close":
                self.alive_time = time.time()
            url, path = split_url(query.URL)
            self.analyzer.add_visitor(url)
            if self.target_connection is None:
                self.target_connection = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
                self.target_connection.connect((sc.gethostbyname(url), 80))
            server_message = HTTPProxyRequest.create_server_request(query, path)
            print("message: " + str(server_message))
            try:
                self.target_connection.send(server_message.to_byte())
            except:
                break
            response = self.read_response()
            print("response: " + str(response))
            if response is None or len(response) == 0:
                break
            try:
                self.connection.send(response)
                self.analyzer.handle_server_packet(HTTP_response_parser(response.decode()))
            except:
                break

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
        headers, tmp_body = self.read_chunck(self.target_connection)
        print("headers: " + str(headers))
        if headers == -1:
            return None
        headers_lines = headers.decode().split("\r\n")[1:]
        is_chunk = False
        content_len = 0
        for line in headers_lines:
            spited = line.split(": ")
            if spited[0] == "Content-Length":
                content_len = int(spited[1])
            elif spited[0] == "Transfer-Encoding" and spited[1] == "chunked":
                is_chunk = True
        print("content: " + str(content_len))
        print("tr_en: " + str(is_chunk))
        body = tmp_body + self.read_body(content_len - len(tmp_body), self.target_connection, is_chunk)
        print("body: " + str(body))
        if body == -1:
            return None
        headers.extend(body)
        return headers

    def read_chunck(self, connection):
        input_data = bytearray()
        while True:
            try:
                connection.settimeout(self.alive_time - time.time())
                data = connection.recv(2048)
                print("in read_chunck: " + data.decode())
                input_data.extend(data)
                if not data or "\r\n\r\n" in input_data.decode():
                    break
            except:
                connection.close()
                return -1, None
        end_header = input_data.find(b"\r\n\r\n")
        return input_data[:end_header + 4], input_data[end_header + 4:]

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
