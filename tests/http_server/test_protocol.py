import pytest
from http_server.models import HTTPRequest, HTTPResponse
from http_server.protocol import build_response, parse_request


@pytest.mark.parametrize(
    "raw_data, expected_method, expected_path, expected_headers",
    [
        (
            b"GET /home HTTP/1.1\r\nHost: localhost\r\n\r\n",
            "GET",
            "/home",
            {"Host": "localhost"},
        ),
        (
            b"POST /api HTTP/1.1\r\nHost: example.com\r\nAccept: */*\r\n\r\n",
            "POST",
            "/api",
            {"Host": "example.com", "Accept": "*/*"},
        ),
        (b"DELETE /old-file HTTP/1.0\r\n\r\n", "DELETE", "/old-file", {}),
    ],
)
def test_parse_request_returns_valid_request_object(
    raw_data: bytes,
    expected_method: str,
    expected_path: str,
    expected_headers: dict[str, str],
):
    request: HTTPRequest = parse_request(raw_data)
    assert request.method == expected_method
    assert request.path == expected_path
    assert request.headers == expected_headers


@pytest.mark.parametrize(
    "response_obj, expected_bytes",
    [
        (
            HTTPResponse(status_code=200, status_text="OK"),
            b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 0\r\n\r\n",
        ),
        (
            HTTPResponse(status_code=404, status_text="Not Found", body="Error!"),
            b"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: 6\r\n\r\nError!",
        ),
        (
            HTTPResponse(
                status_code=200,
                status_text="OK",
                body='{"user": "bartek"}',
                headers={"Content-Type": "application/json"},
            ),
            b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 18\r\n\r\n{"user": "bartek"}',
        ),
    ],
)
def test_build_response_serializes_correctly(
    response_obj: HTTPResponse, expected_bytes: bytes
):
    result: bytes = build_response(response_obj)
    assert result == expected_bytes
