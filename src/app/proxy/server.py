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

    def _get_target_address(self) -> tuple[str, int]:
        """Returns the target backend address. Extracted to allow overriding by Load Balancer."""
        return (self.target_host, self.target_port)

    @override
    def _process_request(
        self, client_socket: socket.socket, address: tuple[str, int]
    ) -> None:
        """Handles bidirectional data streaming between the client and target server using multiplexing (select)."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as target_socket:
            target_address = self._get_target_address()
            try:
                target_socket.connect(target_address)
            except ConnectionRefusedError:
                logger.error(
                    "Backend server %s:%s is down! Connection refused.",
                    target_address[0],
                    target_address[1],
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
