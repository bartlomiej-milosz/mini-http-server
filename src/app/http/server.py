import logging
import socket
from logging import Logger
from typing import Callable, override
from app.tcp.server import TCPServer
from app.http.models import HTTPRequest, HTTPResponse
from app.http.protocol import build_response, parse_request

logger: Logger = logging.getLogger(__name__)


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
