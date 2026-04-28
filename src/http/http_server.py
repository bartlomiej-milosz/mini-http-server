import logging
import socket
from typing import override

from http_response_builder import build_response
from http_response import HTTPResponse
from src.http.http_parser import parse_request
from src.http.http_request import HTTPRequest
from src.tcp_server import TCPServer

logger = logging.getLogger(__name__)


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
    def _handle_client(
            self, client_socket: socket.socket, address: tuple[str, int]
    ) -> None:
        data: bytes = self._receive(client_socket)
        request: HTTPRequest = parse_request(data)
        logger.info("Received %s %s from %s:%s", request.method, request.path, *address)
        response: bytes = build_response(HTTPResponse(200, "OK", "Hello from server!"))
        client_socket.sendall(response)
