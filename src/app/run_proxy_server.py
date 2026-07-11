import logging
import os
from app.proxy.server import ProxyServer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    target_host = os.environ.get("TARGET_HOST", "127.0.0.1")
    target_port = int(os.environ.get("TARGET_PORT", "8001"))

    logger.info("Starting Proxy Server on port 8000 (forwarding to %s:%s)...", target_host, target_port)
    proxy = ProxyServer(host="0.0.0.0", port=8000, target_host=target_host, target_port=target_port)
    proxy.start()
