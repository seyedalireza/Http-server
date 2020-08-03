from HttpServer import HttpServer
from HttpProxyServer import HttpProxyServer
from HttpProxyServer import ProxyAnalyzer
import atexit

if __name__ == "__main__":
    httpServer = HttpServer(8080)
    analyzer = ProxyAnalyzer(8091)
    proxy_server = HttpProxyServer(8090, analyzer)
    try:
        analyzer.setDaemon(True)
        analyzer.start()
        atexit.register(analyzer.stop)

        proxy_server.setDaemon(True)
        proxy_server.start()
        atexit.register(proxy_server.stop)

        httpServer.setDaemon(True)
        httpServer.start()
        atexit.register(httpServer.stop)
        httpServer.join()
        proxy_server.join()
        analyzer.join()
    except KeyboardInterrupt:
        pass
    finally:
        exit(0)
