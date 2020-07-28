from Parser import *
import os
from HP import *
from datetime import datetime
import magic
import gzip


class HTTPResponse(HTTPMessage):
    def __init__(self, status_code, status_message, version=None, connection=None, content_length=None,
                 content_type=None, date=None, body=None):
        super().__init__(connection=connection, version=version)
        self.status_code = status_code
        self.status_msg = status_message
        self.content_len = content_length
        self.content_type = content_type
        self.date = date
        self.body = body

    def __str__(self):
        ret = self.header_str() + str(self.body)
        return ret

    def header_str(self):
        ret = "HTTP/" + str(self.version) + " " + str(self.status_code) + " " + str(self.status_msg) + "\r\n"
        ret = ret + "Connection: " + str(self.connection) + "\r\n"
        ret = ret + "Content-Length: " + str(self.content_len) + "\r\n"
        ret = ret + "Content-Type: " + str(self.content_type) + "\r\n"
        ret = ret + "Date: " + str(self.date) + "\r\n"
        ret = ret + "\r\n"
        return ret

    def to_byte(self):
        ret = self.header_str().encode()
        print(type(ret))
        ret = ret + self.body
        return ret


def response_creator(request_msg):
    """

    :param request_msg: a HTTP Request message.
    :return: An HTTP Response Object. Keep_alive.
    """
    request = HTTP_request_parser(request_msg)
    b = True
    if request is not None and request.URL[0] == '/' and len(request.URL) > 1:
        request.URL = request.URL[1:]
        b = False
    if b and request is not None and request.URL[0] == '/' and len(request.URL) == 1:
        html_file = open(FILES_HTML, "rb")
        response = HTTPResponse(status_code=200, status_message="OK", version=1.0,
                                content_length=os.stat(FILES_HTML).st_size, content_type=TEXT_HTML_TYPE,
                                date=datetime.utcnow(), body=html_file.read())
        html_file.close()
    elif request is None:
        html_file = open(BAD_REQUEST_HTML, "rb")
        response = HTTPResponse(status_code=400, status_message="Bad Request", version=1.0, connection="close",
                                content_length=os.stat(BAD_REQUEST_HTML).st_size, content_type=TEXT_HTML_TYPE,
                                date=datetime.utcnow(), body=html_file.read())
        html_file.close()
    elif request.method not in IMPLEMENTED_METHODS:
        html_file = open(NOT_IMPLEMENTED_HTML, "rb")
        response = HTTPResponse(status_code=501, status_message="Not Implemented", version=1.0, connection="close",
                                content_length=os.stat(NOT_IMPLEMENTED_HTML).st_size, content_type=TEXT_HTML_TYPE,
                                date=datetime.utcnow(), body=html_file.read())
        html_file.close()
    elif request.method != "GET":
        html_file = open(NOT_ALLOWED_HTML, "rb")
        response = HTTPResponse(status_code=405, status_message="Method Not Allowed", version=1.0, connection="close",
                                content_length=os.stat(NOT_ALLOWED_HTML).st_size, content_type=TEXT_HTML_TYPE,
                                date=datetime.utcnow(), body=html_file.read())
        html_file.close()
    elif os.path.isfile(request.URL):
        content_type = magic.from_file(request.URL, mime=True)
        file = open(request.URL, "rb")
        if file is not None:
            body = file.read()
        else:
            body = None
        if body is not None and request.accept_encoding == "gzip":
            body = gzip.compress(body)
        response = HTTPResponse(status_code=200, status_message="OK", version=1.0, connection="close",
                                content_length=os.stat(request.URL).st_size, content_type=content_type,
                                date=datetime.utcnow(), body=body)
    else:
        html_file = open(NOT_FOUND_HTML, "rb")
        response = HTTPResponse(status_code=404, status_message="Not Found", version=1.0, connection="close",
                                content_length=os.stat(NOT_FOUND_HTML).st_size, content_type=NOT_FOUND_HTML,
                                date=datetime.utcnow(), body=html_file.read())
        html_file.close()
    return response, request.keep_alive
