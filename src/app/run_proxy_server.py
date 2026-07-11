import logging
from app.proxy.server import ProxyServer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Proxy Server on port 8000 (forwarding to Load Balancer on 8001)...")
    proxy = ProxyServer(port=8000, target_port=8001)
    proxy.start()
