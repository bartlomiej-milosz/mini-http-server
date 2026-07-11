import logging
import threading
from typing import override
from app.proxy.server import ProxyServer

logger = logging.getLogger(__name__)


class LoadBalancerServer(ProxyServer):
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8001,
        backend_servers: list[tuple[str, int]] | None = None,
    ) -> None:
        """Initializes the Load Balancer Server and configures the backend server pool."""
        super().__init__(host, port, target_host="", target_port=0)
        self.backend_servers = (
            backend_servers
            if backend_servers is not None
            else [("127.0.0.1", 8081), ("127.0.0.1", 8082)]
        )
        self.current_backend_index = 0
        self._lock = threading.Lock()

    @override
    def _get_target_address(self) -> tuple[str, int]:
        """Returns the next backend address using a thread-safe Round Robin algorithm."""
        if not self.backend_servers:
            raise ValueError("No backend servers available in the pool.")

        with self._lock:
            # Pick the current backend
            backend = self.backend_servers[self.current_backend_index]
            # Increment and wrap around
            self.current_backend_index = (self.current_backend_index + 1) % len(
                self.backend_servers
            )

        logger.info("Routing request to backend: %s:%s", *backend)
        return backend
