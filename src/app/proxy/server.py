import logging
import socket
import select
from typing import override

from app.tcp.server import TCPServer

logger = logging.getLogger(__name__)


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

    def _forward_data(self, source: socket.socket, destination: socket.socket) -> bool:
        """Reads a chunk of data from the source socket and sends it to the destination socket. Returns False if disconnected."""
        chunk = source.recv(self.BUFFER_SIZE)
        if not chunk:
            return False
        destination.sendall(chunk)
        return True

    @override
    def _process_request(
        self, client_socket: socket.socket, address: tuple[str, int]
    ) -> None:
        """Handles bidirectional data streaming between the client and target server using multiplexing (select)."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as target_socket:
            try:
                target_socket.connect((self.target_host, self.target_port))
            except ConnectionRefusedError:
                logger.error(
                    "Backend server %s:%s is down! Connection refused.",
                    self.target_host,
                    self.target_port,
                )
                return

            while True:
                ready_to_read, _, _ = select.select(
                    [client_socket, target_socket], [], []
                )
                for ready_socket in ready_to_read:
                    destination = (
                        target_socket
                        if ready_socket is client_socket
                        else client_socket
                    )
                    if not self._forward_data(ready_socket, destination):
                        return
