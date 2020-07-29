import HttpProxyServer
from HttpServer import HttpServer
import logging
import atexit

if __name__ == "__main__":
    # config logging
    # TODO start http proxy server
    httpServer = HttpServer(8080)
    httpServer.setDaemon(True)
    httpServer.start()
    atexit.register(httpServer.stop)
    httpServer.join()
