from Parser import *
import os
from HP import *
from datetime import datetime


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
        ret = "version: " + str(self.version) + " status code: " + str(self.status_code) + " status_message: " + str(
            self.status_msg)
        ret = ret + "\nconnection: " + str(self.connection)
        ret = ret + "\ncontent-length: " + str(self.content_len)
        ret = ret + "\ncontent-type: " + str(self.content_type)
        ret = ret + "\ndate: " + str(self.date)
        ret = ret + "\nbody:\n"
        ret = ret + self.body
        return ret


def response_creator(request_msg):
    """

    :param request_msg: a HTTP Request message.
    :return: An HTTP Response Object.
    """
    request = HTTP_request_parser(request_msg)
    response = None
    if request is None:
        html_file = open(BAD_REQUEST_HTML, "r")
        response = HTTPResponse(status_code=400, status_message="Bad Request", version=1.0, connection="close",
                                content_length=os.stat(BAD_REQUEST_HTML).st_size, content_type=TEXT_HTML_TYPE,
                                date=datetime.utcnow(), body=html_file.read())
        html_file.close()
    elif request.method not in IMPLEMENTED_METHODS:
        html_file = open(NOT_IMPLEMENTED_HTML, "r")
        response = HTTPResponse(status_code=501, status_message="Not Implemented", version=1.0, connection="close",
                                content_length=os.stat(NOT_IMPLEMENTED_HTML).st_size, content_type=TEXT_HTML_TYPE,
                                date=datetime.utcnow(), body=html_file.read())
        html_file.close()
    elif request.method != "GET":
        html_file = open(NOT_ALLOWED_HTML, "r")
        response = HTTPResponse(status_code=405, status_message="Method Not Allowed", version=1.0, connection="close",
                                content_length=os.stat(NOT_ALLOWED_HTML).st_size, content_type=TEXT_HTML_TYPE,
                                date=datetime.utcnow(), body=html_file.read())
        html_file.close()
    # TODO: in case that file doesn't exist or exist.
    return response
