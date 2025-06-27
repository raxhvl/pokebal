import httpx
from typing import Any, Dict, Optional


class HTTPTransport:
    def __init__(
        self, url: str, timeout: float = 30.0, headers: Optional[Dict[str, str]] = None
    ):
        self.url = url
        self.timeout = timeout
        self.custom_headers = headers or {}
        self.client = httpx.Client(timeout=timeout)

    def send(self, request: Dict[str, Any]) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        headers.update(self.custom_headers)

        response = self.client.post(self.url, json=request, headers=headers)

        response.raise_for_status()
        return response.json()

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()
