import logging
import json
from app.http.server import HTTPServer
from app.http.models import HTTPRequest, HTTPResponse

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s"
)


def api_status(request: HTTPRequest) -> HTTPResponse:
    data = {"status": "ok", "version": "1.0", "message": "Backend API is running"}
    return HTTPResponse(
        status_code=200,
        status_text="OK",
        body=json.dumps(data),
        headers={"Content-Type": "application/json"},
    )


def api_users(request: HTTPRequest) -> HTTPResponse:
    data = {"users": ["kate", "admin", "guest"]}
    return HTTPResponse(
        status_code=200,
        status_text="OK",
        body=json.dumps(data),
        headers={"Content-Type": "application/json"},
    )


def api_echo(request: HTTPRequest) -> HTTPResponse:
    return HTTPResponse(
        status_code=200,
        status_text="OK",
        body=request.body,
        headers={"Content-Type": request.headers.get("Content-Type", "text/plain")},
    )


if __name__ == "__main__":
    server = HTTPServer(port=8080)
    server.add_route("GET", "/api/status", api_status)
    server.add_route("GET", "/api/users", api_users)
    server.add_route("POST", "/api/echo", api_echo)
    server.start()
