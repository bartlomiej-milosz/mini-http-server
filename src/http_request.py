from dataclasses import dataclass


@dataclass
class HTTPRequest:
    method: str
    path: str
    version: str
    headers: dict[str, str]
    body: str = ""
