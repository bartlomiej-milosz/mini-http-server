import socket
from typing import override
from app.tcp.server import TCPServer


class LoadBalancerServer(TCPServer):
    def __init__(self, host: str = "127.0.0.1", port: int = 8001) -> None:
        """Initializes the Load Balancer Server and configures the backend server pool."""
        super().__init__(host, port)
        # TODO: Define list of backend servers (e.g. [("127.0.0.1", 8080), ("127.0.0.1", 8081)])
        pass

    @override
    def _process_request(
        self, client_socket: socket.socket, address: tuple[str, int]
    ) -> None:
        """Distributes incoming client requests across the backend servers using a load balancing algorithm."""
        # TODO: Implement load balancing algorithm (e.g. Round Robin) to select a backend server
        pass
