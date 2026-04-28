from src.http.http_request import HTTPRequest


def parse_request(data: bytes) -> HTTPRequest:
    text: str = data.decode("utf-8")
    lines: list[str] = text.split("\r\n")
    method, path, version = lines[0].split()
    headers: dict[str, str] = {}
    for line in lines[1:]:
        header, content = line.split(":", 1)
        headers[header] = content.strip()
    return HTTPRequest(method, path, version, headers)
