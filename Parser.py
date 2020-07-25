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


class HTTPResponse(HTTPMessage):
    def __int__(self, status_code, status_message, version=None, connection=None, content_length=None,
                content_type=None, date=None, body=None):
        super().__init__(connection=connection, version=version)
        self.status_code = status_code
        self.status_msg = status_message
        self.content_len = content_length
        self.content_type = content_type
        self.date = date
        self.body = body
