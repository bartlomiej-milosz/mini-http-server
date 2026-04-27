import socket
from typing import Final


class TCPServer:
    BACKLOG: Final = 5

    def __init__(self, host: str = "127.0.0.1", port: int = 8080) -> None:
        self.host: str = host
        self.port: int = port
        # Create a socket with an explicit IPv4 and TCP specification
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self) -> None:
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.BACKLOG)
        while True:
            address: tuple[str, int]
            client_socket, address = self.server_socket.accept()
            print(f"New connection from {address}")
            client_socket.close()
