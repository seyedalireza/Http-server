import HttpProxyServer
from HttpServer import HttpServer
import logging

if __name__ == "__main__":
    # config logging
    # TODO start http server and http proxy server
    httpServer = HttpServer(8080)
    httpServer.start()
    httpServer.join()
