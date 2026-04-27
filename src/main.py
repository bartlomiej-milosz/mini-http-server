import logging

from src.TCPServer import TCPServer

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s"
)


if __name__ == "__main__":
    server = TCPServer()
    server.start()
