from src.http.http_response import HTTPResponse


def build_response(response: HTTPResponse) -> bytes:
    status_line: str = (
        f"{response.version} {response.status_code} {response.status_text}\r\n"
    )
    response.headers["Content-Length"] = str(len(response.body))
    headers: str = ""
    for key, value in response.headers.items():
        headers += f"{key}: {value}\r\n"
    raw_response: str = status_line + headers + "\r\n" + response.body
    return raw_response.encode("utf-8")
