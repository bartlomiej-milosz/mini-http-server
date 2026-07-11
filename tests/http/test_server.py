import socket
import pytest
from unittest.mock import MagicMock
from pytest_mock import MockerFixture
from app.http.models import HTTPRequest, HTTPResponse
from app.http.server import HTTPServer


@pytest.fixture
def get_http_server() -> HTTPServer:
    return HTTPServer()


@pytest.fixture
def mock_client_socket(mocker: MockerFixture) -> MagicMock:
    return mocker.MagicMock(spec=socket.socket)


class TestHTTPServer:
    def test_receive_stops_at_double_crlf(
        self, get_http_server: HTTPServer, mock_client_socket: MagicMock
    ):
        http_server: HTTPServer = get_http_server
        mock_client_socket.recv.side_effect = [
            b"GET / HTTP/1.1\r\n",
            b"Host: localhost",
            b"\r\n\r\n",
        ]
        result: bytes = http_server._receive(mock_client_socket)
        expected_bytes: bytes = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
        assert result == expected_bytes
        assert mock_client_socket.recv.call_count == 3

    def test_receive_fetches_full_body_based_on_content_length(
        self, get_http_server: HTTPServer, mock_client_socket: MagicMock
    ):
        http_server: HTTPServer = get_http_server
        mock_client_socket.recv.side_effect = [
            b"POST /api HTTP/1.1\r\n",
            b"Content-Length: 10\r\n\r\n",
            b"1234",
            b"5678",
            b"90",
        ]
        result: bytes = http_server._receive(mock_client_socket)
        expected_bytes: bytes = (
            b"POST /api HTTP/1.1\r\nContent-Length: 10\r\n\r\n1234567890"
        )
        assert result == expected_bytes
        assert mock_client_socket.recv.call_count == 5

    def test_add_route_adds_handler_to_routes_dict(self, get_http_server: HTTPServer):
        def dummy_handler(request: HTTPRequest) -> HTTPResponse:
            return HTTPResponse(200, "OK")

        get_http_server.add_route("GET", "/", dummy_handler)

        assert ("GET", "/") in get_http_server.routes
        assert get_http_server.routes[("GET", "/")] == dummy_handler

    def test_process_request_calls_handler_when_route_exists(
        self,
        get_http_server: HTTPServer,
        mock_client_socket: MagicMock,
        mocker: MockerFixture,
    ):
        mocker.patch.object(
            get_http_server, "_receive", return_value=b"GET / HTTP/1.1\r\n\r\n"
        )
        mock_handler = MagicMock()
        mock_handler.return_value = HTTPResponse(200, "OK", "Test body")

        get_http_server.add_route("GET", "/", mock_handler)
        get_http_server._process_request(mock_client_socket, ("127.0.0.1", 54321))

        mock_handler.assert_called_once()
        expected_response = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 9\r\n\r\nTest body"
        mock_client_socket.sendall.assert_called_once_with(expected_response)

    def test_process_request_returns_404_when_route_missing(
        self,
        get_http_server: HTTPServer,
        mock_client_socket: MagicMock,
        mocker: MockerFixture,
    ):
        mocker.patch.object(
            get_http_server, "_receive", return_value=b"GET /unknown HTTP/1.1\r\n\r\n"
        )
        get_http_server._process_request(mock_client_socket, ("127.0.0.1", 54321))

        expected_response = b"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: 18\r\n\r\n404 Page Not Found"
        mock_client_socket.sendall.assert_called_once_with(expected_response)

    def test_process_request_returns_400_on_parse_error(
        self,
        get_http_server: HTTPServer,
        mock_client_socket: MagicMock,
        mocker: MockerFixture,
    ):
        mocker.patch.object(
            get_http_server, "_receive", return_value=b"MALFORMED_REQUEST_DATA\r\n\r\n"
        )
        get_http_server._process_request(mock_client_socket, ("127.0.0.1", 54321))

        expected_response = b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\nContent-Length: 15\r\n\r\n400 Bad Request"
        mock_client_socket.sendall.assert_called_once_with(expected_response)

    def test_process_request_returns_500_on_handler_error(
        self,
        get_http_server: HTTPServer,
        mock_client_socket: MagicMock,
        mocker: MockerFixture,
    ):
        mocker.patch.object(
            get_http_server, "_receive", return_value=b"GET / HTTP/1.1\r\n\r\n"
        )

        def broken_handler(request: HTTPRequest) -> HTTPResponse:
            raise ValueError("Something went wrong!")

        get_http_server.add_route("GET", "/", broken_handler)
        get_http_server._process_request(mock_client_socket, ("127.0.0.1", 54321))

        expected_response = b"HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\nContent-Length: 25\r\n\r\n500 Internal Server Error"
        mock_client_socket.sendall.assert_called_once_with(expected_response)
