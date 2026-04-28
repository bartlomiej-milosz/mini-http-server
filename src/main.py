import logging

from src.http.http_server import HTTPServer

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s"
)


if __name__ == "__main__":
    server = HTTPServer()
    server.start()
