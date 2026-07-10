import pytest
from src.http.http_parser import parse_request

@pytest.mark.parametrize(
    "raw_data, expected_method, expected_path, expected_headers",
    [
        (
            b"GET /home HTTP/1.1\r\nHost: localhost\r\n\r\n", 
            "GET", 
            "/home", 
            {"Host": "localhost"}
        ),
        (
            b"POST /api HTTP/1.1\r\nHost: example.com\r\nAccept: */*\r\n\r\n", 
            "POST", 
            "/api", 
            {"Host": "example.com", "Accept": "*/*"}
        ),
        (
            b"DELETE /old-file HTTP/1.0\r\n\r\n", 
            "DELETE", 
            "/old-file", 
            {}
        )
    ]
)
def test_parse_request(raw_data, expected_method, expected_path, expected_headers):
    request = parse_request(raw_data)
    
    assert request.method == expected_method
    assert request.path == expected_path
    assert request.headers == expected_headers
