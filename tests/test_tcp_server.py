import socket
from logging import Logger
from typing import override
from unittest.mock import MagicMock
import pytest
from pytest_mock import MockerFixture

from src.tcp_server import TCPServer


@pytest.fixture
def server() -> TCPServer:
    class ConcreteTCPServer(TCPServer):
        @override
        def _process_request(
            self, client_socket: socket.socket, address: tuple[str, int]
        ) -> None: ...

    return ConcreteTCPServer()


@pytest.fixture
def mock_client_socket(mocker: MockerFixture) -> MagicMock:
    return mocker.MagicMock(spec=socket.socket)


@pytest.fixture
def mock_server_socket(mocker: MockerFixture) -> MagicMock:
    return mocker.MagicMock(spec=socket.socket)


@pytest.fixture
def client_address() -> tuple[str, int]:
    return "127.0.0.1", 54321


@pytest.mark.parametrize(
    "chunks",
    [
        [b"Hello", b""],
        [b"Hel", b"lo", b""],
        [b"H", b"e", b"l", b"l", b"o", b""],
    ],
)
def test_receive_returns_data(
    server: TCPServer, chunks: list[bytes], mock_client_socket: MagicMock
):
    mock_client_socket.recv.side_effect = chunks
    result: bytes = server._receive(mock_client_socket)
    assert result == b"Hello"


def test_handle_client_closes_socket(
    server: TCPServer,
    mock_client_socket: MagicMock,
    client_address: tuple[str, int],
    mocker: MockerFixture,
):
    mocker.patch.object(server, "_process_request")
    server._handle_client(mock_client_socket, client_address)
    mock_client_socket.close.assert_called_once()


def test_handle_client_closes_socket_after_connection_reset_error(
    server: TCPServer,
    mock_client_socket: MagicMock,
    client_address: tuple[str, int],
    mocker: MockerFixture,
):
    mocker.patch.object(server, "_process_request", side_effect=ConnectionResetError())
    mock_logger: MagicMock = mocker.patch("src.tcp_server.logger")
    server._handle_client(mock_client_socket, client_address)
    mock_logger.warning.assert_called_once_with(
        "Client %s:%s disconnected unexpectedly", *client_address
    )
    mock_client_socket.close.assert_called_once()


def test_handle_client_closes_socket_after_unicode_decode_error(
    server: TCPServer,
    mock_client_socket: MagicMock,
    client_address: tuple[str, int],
    mocker: MockerFixture,
):
    mocker.patch.object(
        server,
        "_process_request",
        side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid byte"),
    )
    mock_logger: MagicMock = mocker.patch("src.tcp_server.logger")
    server._handle_client(mock_client_socket, client_address)
    mock_logger.error.assert_called_once_with(
        "Failed to decode data from %s:%s", *client_address
    )
    mock_client_socket.close.assert_called_once()
