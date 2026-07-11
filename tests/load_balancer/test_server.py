import threading
import pytest

from app.load_balancer.server import LoadBalancerServer

def test_load_balancer_round_robin():
    backends = [("127.0.0.1", 8081), ("127.0.0.1", 8082), ("127.0.0.1", 8083)]
    lb = LoadBalancerServer(backend_servers=backends)
    assert lb._get_target_address() == ("127.0.0.1", 8081)
    assert lb._get_target_address() == ("127.0.0.1", 8082)
    assert lb._get_target_address() == ("127.0.0.1", 8083)
    assert lb._get_target_address() == ("127.0.0.1", 8081)
    assert lb._get_target_address() == ("127.0.0.1", 8082)

def test_load_balancer_empty_backends():
    lb = LoadBalancerServer(backend_servers=[])
    with pytest.raises(ValueError, match="No backend servers available in the pool."):
        lb._get_target_address()

def test_load_balancer_thread_safety():
    backends = [("127.0.0.1", 8081), ("127.0.0.1", 8082), ("127.0.0.1", 8083)]
    lb = LoadBalancerServer(backend_servers=backends)
    results = []
    
    def worker():
        # Each worker makes 1 request
        target = lb._get_target_address()
        results.append(target)
        
    threads = []
    for _ in range(300):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
        
    assert len(results) == 300
    assert results.count(("127.0.0.1", 8081)) == 100
    assert results.count(("127.0.0.1", 8082)) == 100
    assert results.count(("127.0.0.1", 8083)) == 100
