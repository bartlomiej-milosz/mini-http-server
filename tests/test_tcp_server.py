import socket
from unittest.mock import MagicMock
import pytest
from pytest_mock import MockerFixture

from tcp_server import TCPServer


@pytest.fixture
def server() -> TCPServer:
    return TCPServer()


@pytest.fixture
def mock_socket(mocker: MockerFixture) -> MagicMock:
    return mocker.MagicMock(spec=socket.socket)


@pytest.mark.parametrize(
    "chunks",
    [
        [b"Hello", b""],
        [b"Hel", b"lo", b""],
        [b"H", b"e", b"l", b"l", b"o", b""],
    ],
)
def test_receive_returns_data(
    server: TCPServer, mock_socket: MagicMock, chunks: list[bytes]
):
    mock_socket.recv.side_effect = chunks
    result: bytes = server._receive(mock_socket)
    assert result == b"Hello"
