from HP import *


class HTTPMessage:
    def __init__(self, version=None, connection=None):
        self.connection = connection
        self.version = version


class HTTPRequest(HTTPMessage):
    def __init__(self, method, URL, version=None, connection=None, keep_alive=None, accept_encoding=None, body=None):
        super().__init__(connection=connection, version=version)
        self.method = method
        self.URL = URL
        self.keep_alive = keep_alive
        self.accept_encoding = accept_encoding
        self.body = body

    def __str__(self):
        ret = "method: " + str(self.method) + " URL: " + str(self.URL) + " version: " + str(
            self.version)
        ret = ret + "\nconnection: " + str(self.connection)
        ret = ret + "\nkeep-alive: " + str(self.keep_alive)
        ret = ret + "\naccept-encoding: " + str(self.accept_encoding)
        ret = ret + "\nbody: " + str(self.body)
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
    connection = None
    keep_alive = None
    accept_encoding = None
    for i in range(len(headers)):
        h = headers[i]
        if h[0] == CONNECTION_HEADER:
            if h[1] != "close" and h[1] != "keep-alive":
                raise Exception
            connection = h[1]
            for tmp_h in headers:
                if tmp_h[0] == KEEP_ALIVE_HEADER:
                    try:
                        keep_alive = int(tmp_h[1])
                    except ValueError:
                        keep_alive = DEFAULT_KEEP_ALIVE_TIME
                    break
        elif h[0] == ACCEPT_ENCODING_HEADER:
            tmp = h[1].split(', ')
            if "gzip" in h[1]:
                accept_encoding = "gzip"
    http_req_retv = HTTPRequest(method=method, URL=URL, version=version, connection=connection, keep_alive=keep_alive,
                                accept_encoding=accept_encoding, body=parts[-1])
    return http_req_retv
