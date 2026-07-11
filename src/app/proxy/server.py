import socket
from typing import override

from app.tcp.server import TCPServer


class ProxyServer(TCPServer):
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        target_host: str = "127.0.0.1",
        target_port: int = 8080,
    ) -> None:
        super().__init__(host, port)
        self.target_host = target_host
        self.target_port = target_port

    @override
    def _receive(self, client_socket: socket.socket) -> bytes:
        # TODO: Implement receiving data from the client (browser)
        return b""

    @override
    def _process_request(
        self, client_socket: socket.socket, address: tuple[str, int]
    ) -> None:
        # TODO: Implement proxy logic
        # 1. Read raw bytes from client_socket
        # 2. Open a new socket and connect to self.target_host:self.target_port
        # 3. Send the received bytes to the target server
        # 4. Receive the response from the target server
        # 5. Send the response back to client_socket (browser)
        pass
