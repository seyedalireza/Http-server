from HttpServer import HttpServer
from HttpProxyServer import HttpProxyServer
import atexit

if __name__ == "__main__":
    httpServer = HttpServer(8080)
    proxy_server = HttpProxyServer(8090)
    try:
        # TODO start http proxy server
        proxy_server.setDaemon(True)
        proxy_server.start()
        atexit.register(proxy_server.stop)

        httpServer.setDaemon(True)
        httpServer.start()
        atexit.register(httpServer.stop)
        httpServer.join()
        proxy_server.join()
    except KeyboardInterrupt:
        pass
    finally:
        exit(0)
