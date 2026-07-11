from app.http.models import HTTPRequest, HTTPResponse


def parse_request(data: bytes) -> HTTPRequest:
    """Parses raw HTTP request bytes into an HTTPRequest object."""
    parts = data.split(b"\r\n\r\n", 1)
    header_data = parts[0]
    body_data = parts[1] if len(parts) > 1 else b""

    text: str = header_data.decode("utf-8")
    lines: list[str] = text.split("\r\n")
    method, path, version = lines[0].split()
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if line == "":
            break
        header, content = line.split(":", 1)
        headers[header] = content.strip()
    return HTTPRequest(method, path, version, headers, body_data.decode("utf-8"))


def build_response(response: HTTPResponse) -> bytes:
    """Serializes an HTTPResponse object into raw bytes ready for transmission."""
    status_line: str = (
        f"{response.version} {response.status_code} {response.status_text}\r\n"
    )
    response.headers["Content-Length"] = str(len(response.body))
    headers: str = ""
    for key, value in response.headers.items():
        headers += f"{key}: {value}\r\n"
    raw_response: str = status_line + headers + "\r\n" + response.body
    return raw_response.encode("utf-8")
