from dataclasses import dataclass, field


@dataclass
class HTTPResponse:
    status_code: int
    status_text: str
    body: str = ""
    headers: dict[str, str] = field(default_factory=lambda: {"Content-Type": "text/plain"})
    version: str = "HTTP/1.1"
