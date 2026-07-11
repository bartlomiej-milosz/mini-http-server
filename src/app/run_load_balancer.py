import logging
from app.load_balancer.server import LoadBalancerServer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    backends = [("127.0.0.1", 8081), ("127.0.0.1", 8082), ("127.0.0.1", 8083)]
    
    logger.info("Starting Load Balancer on port 8001 (routing to 8081, 8082, 8083)...")
    lb = LoadBalancerServer(port=8001, backend_servers=backends)
    lb.start()
