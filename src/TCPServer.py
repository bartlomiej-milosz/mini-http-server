import logging
import socket
from typing import Final

logger = logging.getLogger(__name__)


class TCPServer:
    BACKLOG: Final = 5
    BUFFER_SIZE: Final = 1024
    ENCODING: Final = "utf-8"

    def __init__(self, host: str = "127.0.0.1", port: int = 8080) -> None:
        self.host: str = host
        self.port: int = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def _get_socket_data_stream(self, client_socket: socket.socket) -> bytes:
        data: bytes = b""
        while True:
            chunk: bytes = client_socket.recv(self.BUFFER_SIZE)
            if not chunk:
                break
            data += chunk
        return data

    def _handle_client(
        self, client_socket: socket.socket, address: tuple[str, int]
    ) -> None:
        try:
            data: bytes = self._get_socket_data_stream(client_socket)
            logger.info("Received from %s:%s\n%s", *address, data.decode(self.ENCODING))
        except ConnectionResetError:
            logger.warning("Client %s:%s disconnected unexpectedly", *address)
        except UnicodeDecodeError:
            logger.error("Failed to decode data from %s:%s", *address)
        finally:
            client_socket.close()
            logger.info("Client %s:%s disconnected", *address)

    def start(self) -> None:
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.BACKLOG)
        logger.info("The server is listening on: %s:%s", self.host, self.port)
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                logger.info("New connection from %s:%s", *address)
                self._handle_client(client_socket, address)
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        finally:
            self.server_socket.close()
