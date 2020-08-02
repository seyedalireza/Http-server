class HTTPRequest:
    def __init__(self, method, URL, version=None, headers=None, body=None):
        self.method = method
        self.URL = URL
        self.body = body
        self.version = version
        self.headers = headers

    def __str__(self):
        ret = "method: " + str(self.method) + " URL: " + str(self.URL) + " version: " + str(
            self.version)
        ret = ret + "\nconnection: " + str(self.connection)
        ret = ret + "\nkeep-alive: " + str(self.keep_alive)
        ret = ret + "\naccept-encoding: " + str(self.accept_encoding)
        ret = ret + "\nbody: " + str(self.body)
        return ret

    @staticmethod
    def create_server_request(request, path: str):
        new = HTTPRequest(path, request.method, request.version, body=request.body)
        new.headers = request.headers
        if "Proxy-Connection" in request.headers:
            new.headers["Connection"] = request.headers["Proxy-Connection"]
            del new.headers["Proxy-Connection"]
        return new


class HTTPProxyMessage:
    def __init__(self, status_code, status_message, version=None, headers=None, body=None):
        self.status_code = status_code
        self.status_msg = status_message
        self.headers = headers
        self.body = body
        self.version = version

    def __str__(self):
        ret = self.header_str() + str(self.body)
        return ret

    def header_str(self):
        ret = "HTTP/" + str(self.version) + " " + str(self.status_code) + " " + str(self.status_msg) + "\r\n"
        for header, value in self.headers:
            ret = ret + str(header) + ": " + str(value) + "\r\n"
        ret = ret + "\r\n"
        return ret

    def to_byte(self):
        ret = self.header_str().encode()
        ret = ret + self.body
        return ret


def get_version(param):
    """

    :param param: a string from version position of a HTTPMessage(request or response).
    :return: string doesn't obey "HTTP/[float number]" format, None; Otherwise,
    that float number.
    """
    s = param.split('/')
    if len(s) != 2 or s[0] != "HTTP":
        return None
    try:
        float(s[1])
    except ValueError:
        return None
    return float(s[1])


def HTTP_request_parser(msg):
    """

    :param msg: An HTTP Request, received in the Server from a client.
    :return: A HTTPRequest object contains values in received http request. If the
    headers or first line doesn't obey the standard pattern (400 Bad Request), the
    function return None.
    """

    def request_line_parser(line):
        tmp = line.split(' ')
        if len(tmp) >= 3:
            v = get_version(tmp[2])
        if len(tmp) != 3 or len(tmp[0]) == 0 or len(tmp[1]) == 0 or v is None:
            return False, None, None, None
        return True, tmp[0], tmp[1], v

    parts = msg.split("\r\n")
    if len(parts) >= 3:
        ok, method, URL, version = request_line_parser(parts[0])
        if not ok:
            return None
    else:
        return None
    headers = []
    for i in range(1, len(parts) - 2):
        if not (": " in parts[i]):
            return None
        tmp = parts[i].split(": ")
        headers.append([tmp[0], parts[i][len(tmp[0]) + 2:]])
    http_req_retv = HTTPRequest(method=method, URL=URL, version=version, headers=headers,
                                body=parts[-1])
    return http_req_retv
