import logging
import socket
import threading
from abc import ABC, abstractmethod
from logging import Logger
from typing import Final

logger: Logger = logging.getLogger(__name__)


class TCPServer(ABC):
    BACKLOG: Final = 5
    BUFFER_SIZE: Final = 1024

    def __init__(self, host: str = "127.0.0.1", port: int = 8080) -> None:
        self.host: str = host
        self.port: int = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    @abstractmethod
    def _process_request(
        self, client_socket: socket.socket, address: tuple[str, int]
    ) -> None:
        """Abstract method to handle raw incoming data from a client socket."""
        ...

    def _handle_client(
        self, client_socket: socket.socket, address: tuple[str, int]
    ) -> None:
        """Wrapper method executed in a separate thread to manage client lifecycle and error handling."""
        try:
            self._process_request(client_socket, address)
        except ConnectionResetError:
            logger.warning("Client %s:%s disconnected unexpectedly", *address)
        except UnicodeDecodeError:
            logger.error("Failed to decode data from %s:%s", *address)
        finally:
            client_socket.close()
            logger.info("Client %s:%s disconnected", *address)

    def start(self) -> None:
        """Binds the socket to the port and starts listening for incoming connections in an infinite loop."""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.BACKLOG)
        logger.info("The server is listening on: %s:%s", self.host, self.port)
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                logger.info("New connection from %s:%s", *address)
                threading.Thread(
                    target=self._handle_client, args=(client_socket, address)
                ).start()
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        finally:
            self.server_socket.close()
