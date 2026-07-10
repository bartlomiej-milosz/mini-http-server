import logging
import socket
from abc import ABC, abstractmethod
from logging import Logger
from typing import Final, override

from http_server.models import HTTPRequest, HTTPResponse
from http_server.protocol import build_response, parse_request

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
    def _receive(self, client_socket: socket.socket) -> bytes: ...

    @abstractmethod
    def _process_request(
        self, client_socket: socket.socket, address: tuple[str, int]
    ) -> None: ...

    def _handle_client(
        self, client_socket: socket.socket, address: tuple[str, int]
    ) -> None:
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


class HTTPServer(TCPServer):
    @override
    def _receive(self, client_socket: socket.socket) -> bytes:
        data: bytes = b""
        while True:
            chunk: bytes = client_socket.recv(self.BUFFER_SIZE)
            data += chunk
            # HTTP header termination
            if b"\r\n\r\n" in data:
                break
        return data

    @override
    def _process_request(
        self, client_socket: socket.socket, address: tuple[str, int]
    ) -> None:
        data: bytes = self._receive(client_socket)
        request: HTTPRequest = parse_request(data)
        logger.info("Received %s %s from %s:%s", request.method, request.path, *address)
        response: bytes = build_response(HTTPResponse(200, "OK", "Hello from server!"))
        client_socket.sendall(response)
