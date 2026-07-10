# mini-http-server

A minimal HTTP/1.1 server built from scratch in Python using raw sockets — no frameworks, no standard library `http` module.

## Architecture

The server is split into two layers:

- **`TCPServer`** — abstract base class that manages the socket lifecycle (bind, listen, accept, close) and connection error handling.
- **`HTTPServer`** — concrete subclass that overrides request receiving (stops at `\r\n\r\n`) and request processing (parse → respond).

```
http_server/
├── main.py            # Entry point
├── server.py          # TCPServer and HTTPServer
├── models.py          # HTTPRequest and HTTPResponse dataclasses
└── protocol.py        # HTTP parsing and building logic
```

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv)

## Setup

```sh
uv sync
```

## Running

```sh
uv run python -m http_server.main
```

The server starts on `127.0.0.1:8080` by default. Every incoming request receives a `200 OK` response with the body `Hello from server!`.

```sh
curl http://localhost:8080
```

## Testing

```sh
uv run pytest
```

With coverage:

```sh
uv run pytest --cov=http_server
```

## Linting & type checking

```sh
uv run ruff check
uv run ty check
```
