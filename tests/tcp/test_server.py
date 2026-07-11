import socket
from typing import override
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from app.tcp.server import TCPServer


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
        mock_logger: MagicMock = mocker.patch("app.tcp.server.logger")
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
        mock_logger: MagicMock = mocker.patch("app.tcp.server.logger")
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
        mock_logger = mocker.patch("app.tcp.server.logger")
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
        mock_logger: MagicMock = mocker.patch("app.tcp.server.logger")
        started_server.start()
        mock_logger.info.assert_any_call("New connection from %s:%s", *client_address)

    def test_server_closes_socket_after_keyboard_interrupt(
        self,
        started_server: TCPServer,
        mock_server_socket: MagicMock,
    ):
        started_server.start()
        mock_server_socket.close.assert_called_once()
