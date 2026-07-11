import socket
from typing import override
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from http_server.models import HTTPRequest, HTTPResponse
from http_server.server import HTTPServer, TCPServer


@pytest.fixture
def get_tcp_server() -> TCPServer:
    class ConcreteTCPServer(TCPServer):
        @override
        def _receive(self, client_socket: socket.socket) -> bytes:
            data: bytes = b""
            while True:
                chunk: bytes = client_socket.recv(self.BUFFER_SIZE)
                if not chunk:
                    break
                data += chunk
            return data

        @override
        def _process_request(
            self, client_socket: socket.socket, address: tuple[str, int]
        ) -> None: ...

    return ConcreteTCPServer()


@pytest.fixture
def get_http_server() -> HTTPServer:
    return HTTPServer()


@pytest.fixture
def started_server(
    get_tcp_server, mock_server_socket, mock_client_socket, client_address, mocker
):
    get_tcp_server.server_socket = mock_server_socket
    mocker.patch.object(get_tcp_server, "_handle_client")
    mock_server_socket.accept.side_effect = [
        (mock_client_socket, client_address),
        KeyboardInterrupt(),
    ]
    return get_tcp_server


@pytest.fixture
def mock_client_socket(mocker: MockerFixture) -> MagicMock:
    return mocker.MagicMock(spec=socket.socket)


@pytest.fixture
def mock_server_socket(mocker: MockerFixture) -> MagicMock:
    return mocker.MagicMock(spec=socket.socket)


@pytest.fixture
def client_address() -> tuple[str, int]:
    return "127.0.0.1", 54321


@pytest.fixture
def server_address() -> tuple[str, int]:
    return "127.0.0.1", 8080


class TestTCPServer:
    @pytest.mark.parametrize(
        "chunks",
        [
            [b"Hello", b""],
            [b"Hel", b"lo", b""],
            [b"H", b"e", b"l", b"l", b"o", b""],
        ],
    )
    def test_receive_returns_data(
        self,
        get_tcp_server: TCPServer,
        chunks: list[bytes],
        mock_client_socket: MagicMock,
    ):
        mock_client_socket.recv.side_effect = chunks
        result: bytes = get_tcp_server._receive(mock_client_socket)
        assert result == b"Hello"

    def test_handle_client_closes_socket(
        self,
        get_tcp_server: TCPServer,
        mock_client_socket: MagicMock,
        client_address: tuple[str, int],
        mocker: MockerFixture,
    ):
        mocker.patch.object(get_tcp_server, "_process_request")
        get_tcp_server._handle_client(mock_client_socket, client_address)
        mock_client_socket.close.assert_called_once()

    def test_handle_client_closes_socket_after_connection_reset_error(
        self,
        get_tcp_server: TCPServer,
        mock_client_socket: MagicMock,
        client_address: tuple[str, int],
        mocker: MockerFixture,
    ):
        mocker.patch.object(
            get_tcp_server, "_process_request", side_effect=ConnectionResetError()
        )
        mock_logger: MagicMock = mocker.patch("http_server.server.logger")
        get_tcp_server._handle_client(mock_client_socket, client_address)
        mock_logger.warning.assert_called_once_with(
            "Client %s:%s disconnected unexpectedly", *client_address
        )
        mock_client_socket.close.assert_called_once()

    def test_handle_client_closes_socket_after_unicode_decode_error(
        self,
        get_tcp_server: TCPServer,
        mock_client_socket: MagicMock,
        client_address: tuple[str, int],
        mocker: MockerFixture,
    ):
        mocker.patch.object(
            get_tcp_server,
            "_process_request",
            side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid byte"),
        )
        mock_logger: MagicMock = mocker.patch("http_server.server.logger")
        get_tcp_server._handle_client(mock_client_socket, client_address)
        mock_logger.error.assert_called_once_with(
            "Failed to decode data from %s:%s", *client_address
        )
        mock_client_socket.close.assert_called_once()

    def test_server_binds_correct_address(
        self,
        get_tcp_server: TCPServer,
        mock_server_socket: MagicMock,
        server_address: tuple[str, int],
    ):
        get_tcp_server.server_socket = mock_server_socket
        mock_server_socket.accept.side_effect = KeyboardInterrupt()
        get_tcp_server.start()
        mock_server_socket.bind.assert_called_once_with(server_address)

    def test_server_listens_with_correct_backlog(
        self,
        get_tcp_server: TCPServer,
        mock_server_socket: MagicMock,
    ):
        get_tcp_server.server_socket = mock_server_socket
        mock_server_socket.accept.side_effect = KeyboardInterrupt()
        get_tcp_server.start()
        mock_server_socket.listen.assert_called_once_with(TCPServer.BACKLOG)

    def test_server_logs_listening_address(
        self,
        get_tcp_server: TCPServer,
        mock_server_socket: MagicMock,
        server_address: tuple[str, int],
        mocker: MockerFixture,
    ):
        get_tcp_server.server_socket = mock_server_socket
        mock_logger = mocker.patch("http_server.server.logger")
        mock_server_socket.accept.side_effect = KeyboardInterrupt()
        get_tcp_server.start()
        mock_logger.info.assert_any_call(
            "The server is listening on: %s:%s", *server_address
        )

    def test_server_accepts_client_socket_and_address(
        self,
        started_server: TCPServer,
        client_address: tuple[str, int],
        mocker: MockerFixture,
    ):
        mock_logger: MagicMock = mocker.patch("http_server.server.logger")
        started_server.start()
        mock_logger.info.assert_any_call("New connection from %s:%s", *client_address)

    def test_server_closes_socket_after_keyboard_interrupt(
        self,
        started_server: TCPServer,
        mock_server_socket: MagicMock,
    ):
        started_server.start()
        mock_server_socket.close.assert_called_once()


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

    def test_add_route_adds_handler_to_routes_dict(self, get_http_server: HTTPServer):
        def dummy_handler(request: HTTPRequest) -> HTTPResponse: ...

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
