from dataclasses import dataclass, field


@dataclass
class HTTPRequest:
    method: str
    path: str
    version: str
    headers: dict[str, str]
    body: str = ""


@dataclass
class HTTPResponse:
    status_code: int
    status_text: str
    body: str = ""
    headers: dict[str, str] = field(
        default_factory=lambda: {"Content-Type": "text/plain"}
    )
    version: str = "HTTP/1.1"
