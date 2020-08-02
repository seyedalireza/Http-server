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
        print(type(ret))
        ret = ret + self.body
        return ret
