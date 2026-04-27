import socket
from typing import override

from src.tcp_server import TCPServer


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
    
    # @override
    # def _handle_client(
    #     self, client_socket: socket.socket, address: tuple[str, int]
    # ) -> None:
    #     pass
