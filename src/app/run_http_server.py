import logging
import json
import sys
from app.http.server import HTTPServer
from app.http.models import HTTPRequest, HTTPResponse

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s"
)


def get_api_status(port: int):
    def api_status(request: HTTPRequest) -> HTTPResponse:
        """Health check endpoint returning the status and version of the API."""
        data = {
            "status": "ok",
            "version": "1.0",
            "message": f"Backend API is running on port {port}",
        }
        return HTTPResponse(
            status_code=200,
            status_text="OK",
            body=json.dumps(data),
            headers={"Content-Type": "application/json"},
        )

    return api_status


def api_users(request: HTTPRequest) -> HTTPResponse:
    """Mock endpoint returning a static list of system users."""
    data = {"users": ["kate", "admin", "guest"]}
    return HTTPResponse(
        status_code=200,
        status_text="OK",
        body=json.dumps(data),
        headers={"Content-Type": "application/json"},
    )


def api_echo(request: HTTPRequest) -> HTTPResponse:
    """Echo endpoint that returns the received request body exactly as it was sent."""
    return HTTPResponse(
        status_code=200,
        status_text="OK",
        body=request.body,
        headers={"Content-Type": request.headers.get("Content-Type", "text/plain")},
    )


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    server = HTTPServer(host="0.0.0.0", port=port)
    server.add_route("GET", "/api/status", get_api_status(port))
    server.add_route("GET", "/api/users", api_users)
    server.add_route("POST", "/api/echo", api_echo)
    server.start()
