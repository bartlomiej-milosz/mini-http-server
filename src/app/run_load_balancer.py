import logging
import os
from app.load_balancer.server import LoadBalancerServer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    backends_env = os.environ.get("BACKEND_SERVERS")
    if backends_env:
        # Expected format: "host1:port1,host2:port2"
        backends = []
        for server in backends_env.split(","):
            host, port = server.split(":")
            backends.append((host, int(port)))
    else:
        backends = [("127.0.0.1", 8081), ("127.0.0.1", 8082), ("127.0.0.1", 8083)]
    
    logger.info("Starting Load Balancer on port 8001 (routing to %s)...", backends)
    lb = LoadBalancerServer(host="0.0.0.0", port=8001, backend_servers=backends)
    lb.start()
