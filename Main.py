from HttpServer import HttpServer
import atexit

if __name__ == "__main__":
    httpServer = HttpServer(8080)
    try:
        # TODO start http proxy server
        httpServer.setDaemon(True)
        httpServer.start()
        atexit.register(httpServer.stop)
        httpServer.join()
    except KeyboardInterrupt:
        pass
    finally:
        exit(0)