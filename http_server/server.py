import logging
import socket
import threading
from abc import ABC, abstractmethod
from logging import Logger
from typing import Callable, Final, override

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
                threading.Thread(
                    target=self._handle_client, args=(client_socket, address)
                ).start()
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        finally:
            self.server_socket.close()


class HTTPServer(TCPServer):
    def __init__(self, host: str = "127.0.0.1", port: int = 8080) -> None:
        super().__init__(host, port)
        self.routes: dict[tuple[str, str], Callable[[HTTPRequest], HTTPResponse]] = {}

    def add_route(
        self, method: str, path: str, handler: Callable[[HTTPRequest], HTTPResponse]
    ):
        self.routes[(method, path)] = handler

    def _read_until_headers_complete(self, client_socket: socket.socket) -> bytes:
        data: bytes = b""
        while b"\r\n\r\n" not in data:
            chunk: bytes = client_socket.recv(self.BUFFER_SIZE)
            if not chunk:
                break
            data += chunk
        return data

    def _extract_content_length(self, headers_raw: bytes) -> int:
        headers_text: str = headers_raw.decode("utf-8", errors="ignore")
        for line in headers_text.split("\r\n")[1:]:
            if ":" in line:
                key, val = line.split(":", 1)
                if key.strip().lower() == "content-length":
                    try:
                        return int(val.strip())
                    except ValueError:
                        return 0
        return 0

    def _read_body_by_content_length(
        self, client_socket: socket.socket, body_raw: bytes, content_length: int
    ) -> bytes:
        while len(body_raw) < content_length:
            chunk: bytes = client_socket.recv(self.BUFFER_SIZE)
            if not chunk:
                break
            body_raw += chunk
        return body_raw

    @override
    def _receive(self, client_socket: socket.socket) -> bytes:
        data: bytes = self._read_until_headers_complete(client_socket)

        if b"\r\n\r\n" not in data:
            return data

        headers_raw, initial_body_raw = data.split(b"\r\n\r\n", 1)
        content_length: int = self._extract_content_length(headers_raw)

        full_body_raw: bytes = self._read_body_by_content_length(
            client_socket, initial_body_raw, content_length
        )

        return headers_raw + b"\r\n\r\n" + full_body_raw

    def _send_response(
        self, client_socket: socket.socket, response: HTTPResponse
    ) -> None:
        encoded_response: bytes = build_response(response)
        client_socket.sendall(encoded_response)

    def _dispatch_request(self, request: HTTPRequest) -> HTTPResponse:
        route_key: tuple[str, str] = (request.method, request.path)
        if route_key not in self.routes:
            return HTTPResponse(404, "Not Found", "404 Page Not Found")

        handler: Callable[[HTTPRequest], HTTPResponse] = self.routes[route_key]
        try:
            return handler(request)
        except Exception as e:
            logger.error("Handler error on %s: %s", request.path, e)
            return HTTPResponse(
                500, "Internal Server Error", "500 Internal Server Error"
            )

    @override
    def _process_request(
        self, client_socket: socket.socket, address: tuple[str, int]
    ) -> None:
        data: bytes = self._receive(client_socket)

        try:
            request: HTTPRequest = parse_request(data)
        except Exception as e:
            logger.error("Failed to parse request: %s", e)
            self._send_response(
                client_socket, HTTPResponse(400, "Bad Request", "400 Bad Request")
            )
            return

        logger.info("Received %s %s from %s:%s", request.method, request.path, *address)
        response: HTTPResponse = self._dispatch_request(request)
        self._send_response(client_socket, response)
