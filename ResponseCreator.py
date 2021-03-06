from Parser import *
import os
from HP import *
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import magic
import gzip


class HTTPResponse(HTTPMessage):
    def __init__(self, status_code, status_message, version=None, connection=None, content_length=None,
                 content_type=None, date=format_date_time(mktime(datetime.now().timetuple())), body=None,
                 content_encoding=None):
        super().__init__(connection=connection, version=version)
        self.status_code = status_code
        self.status_msg = status_message
        self.content_len = content_length
        self.content_type = content_type
        self.date = date
        self.body = body
        self.content_encoding = content_encoding

    def __str__(self):
        ret = self.header_str() + str(self.body)
        return ret

    def header_str(self):
        ret = "HTTP/" + str(self.version) + " " + str(self.status_code) + " " + str(self.status_msg) + "\r\n"
        ret = ret + "Connection: " + str(self.connection) + "\r\n"
        ret = ret + "Content-Length: " + str(self.content_len) + "\r\n"
        ret = ret + "Content-Type: " + str(self.content_type) + "\r\n"
        ret = ret + "Date: " + str(self.date) + "\r\n"
        if self.content_encoding is not None:
            ret = ret + "Content-Encoding: " + str(self.content_encoding) + "\r\n"
        ret = ret + "\r\n"
        return ret

    def to_byte(self):
        ret = self.header_str().encode()
        ret = ret + self.body
        return ret


def response_creator(request_msg):
    """

    :param request_msg: a HTTP Request message.
    :return: An HTTP Response Object. Keep_alive.
    """
    request = HTTP_request_parser(request_msg)
    b = True
    response_time = format_date_time(mktime(datetime.now().timetuple()))
    if request is not None and request.URL[0] == '/' and len(request.URL) > 1:
        request.URL = request.URL[1:]
        b = False
    if request is None:
        html_file = open(BAD_REQUEST_HTML, "rb")
        response = HTTPResponse(status_code=400, status_message="Bad Request", version=1.0, connection="close",
                                content_length=os.stat(BAD_REQUEST_HTML).st_size, content_type=TEXT_HTML_TYPE,
                                date=response_time, body=html_file.read())
        html_file.close()
    elif request.method not in IMPLEMENTED_METHODS:
        html_file = open(NOT_IMPLEMENTED_HTML, "rb")
        response = HTTPResponse(status_code=501, status_message="Not Implemented", version=1.0, connection="close",
                                content_length=os.stat(NOT_IMPLEMENTED_HTML).st_size, content_type=TEXT_HTML_TYPE,
                                date=response_time, body=html_file.read())
        html_file.close()
    elif request.method != "GET":
        html_file = open(NOT_ALLOWED_HTML, "rb")
        response = HTTPResponse(status_code=405, status_message="Method Not Allowed", version=1.0, connection="close",
                                content_length=os.stat(NOT_ALLOWED_HTML).st_size, content_type=TEXT_HTML_TYPE,
                                date=response_time, body=html_file.read())
        html_file.close()
    elif b and request is not None and request.URL[0] == '/' and len(request.URL) == 1:
        html_file = open(FILES_HTML, "rb")
        response = HTTPResponse(status_code=200, status_message="OK", version=1.0,
                                content_length=os.stat(FILES_HTML).st_size, content_type=TEXT_HTML_TYPE,
                                date=response_time, body=html_file.read())
        html_file.close()
    elif os.path.isfile("files/" + request.URL):
        request.URL = "files/" + request.URL
        content_type = magic.from_file(request.URL, mime=True)
        file = open(request.URL, "rb")
        if file is not None:
            body = file.read()
        else:
            body = None
        content_encoding = None
        content_length = os.stat(request.URL).st_size
        if body is not None and request.accept_encoding == "gzip":
            body = gzip.compress(body)
            content_encoding = "gzip"
            content_length = len(body)
        response = HTTPResponse(status_code=200, status_message="OK", version=1.0, connection="close",
                                content_length=content_length, content_type=content_type,
                                date=response_time, body=body, content_encoding=content_encoding)
    else:
        html_file = open(NOT_FOUND_HTML, "rb")
        response = HTTPResponse(status_code=404, status_message="Not Found", version=1.0, connection="close",
                                content_length=os.stat(NOT_FOUND_HTML).st_size, content_type=NOT_FOUND_HTML,
                                date=response_time, body=html_file.read())
        html_file.close()
    keep_alive = None
    if request is not None:
        keep_alive = request.keep_alive
    return response, keep_alive
