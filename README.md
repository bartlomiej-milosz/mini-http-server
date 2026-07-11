# raw-network-stack

A complete networking stack built from scratch in Python using raw sockets — no frameworks, no standard library networking modules.

This project is an educational and architectural showcase demonstrating how to build a highly symmetric, decoupled system capable of handling HTTP traffic, proxying requests, and load balancing across multiple server instances.

## Architecture

The project is structured into logical, decoupled layers within the `src/app` package (following the standard Python `src/` layout). It heavily utilizes Object-Oriented Programming and abstraction to maintain a clean architecture.

```text
raw-network-stack/
├── src/
│   └── app/
│       ├── main.py            # Entry point for the application
│       ├── tcp/               # Base Networking Layer
│       │   └── server.py      # Abstract TCPServer (bind, listen, accept)
│       ├── http/              # HTTP Protocol Layer
│       │   ├── server.py      # Concrete HTTPServer and Routing
│       │   ├── models.py      # HTTPRequest and HTTPResponse dataclasses
│       │   └── protocol.py    # HTTP parsing and payload building logic
│       ├── proxy/             # Gateway Layer
│       │   └── server.py      # Reverse Proxy implementation
│       └── load_balancer/     # Traffic Management Layer
│           └── server.py      # Load Balancer stub (future implementation)
└── tests/                     # Comprehensive Pytest Suite
```

### Components

1. **`TCPServer`**: The foundation of the stack. An abstract base class managing socket lifecycles, threading, and safe client connection handling.
2. **`HTTPServer`**: Inherits from `TCPServer`. Handles HTTP/1.1 parsing, header reading, payload extraction (via `Content-Length`), and dispatches requests to defined routes.
3. **`ProxyServer`**: Inherits from `TCPServer`. Designed to act as an intermediary, forwarding raw socket data between clients and backend servers.
4. **`LoadBalancerServer`**: Inherits from `TCPServer`. Designed to distribute incoming TCP traffic across multiple backend `HTTPServer` instances using algorithms like Round Robin.

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (Extremely fast Python package installer and resolver)

## Setup

Initialize the virtual environment and install dependencies:

```sh
uv sync
```

## Running the Server

Start the HTTP server on `127.0.0.1:8080`:

```sh
uv run python -m app.main
```

Test it by sending a curl request:

```sh
curl http://localhost:8080
```

## Testing and QA

The project maintains rigorous code quality and high test coverage.

**Run unit tests:**

```sh
uv run pytest
```

**Run tests with coverage:**

```sh
uv run pytest --cov=app
```

**Linting and Type Checking:**

```sh
uv run ruff check
uv run ty check
```

## CI / CD

The project is integrated with GitHub Actions. Every push automatically triggers a pipeline that:

1. Installs the environment using `uv`.
2. Runs the `ruff` linter.
3. Validates static types using `ty`.
4. Executes the full `pytest` suite.
