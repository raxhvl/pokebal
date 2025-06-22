from typing import Any, Dict, Optional
from .transport import HTTPTransport


class RPCClient:
    def __init__(self, transport: HTTPTransport):
        self.transport = transport
        self._request_id = 0

    def _next_request_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def call(self, method: str, params: Optional[list] = None) -> Any:
        if params is None:
            params = []

        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": method,
            "params": params,
        }

        response = self.transport.send(request)

        if "error" in response:
            raise RPCError(response["error"])

        return response.get("result")


class RPCError(Exception):
    def __init__(self, error_data: Dict[str, Any]):
        self.code = error_data.get("code")
        self.message = error_data.get("message")
        self.data = error_data.get("data")
        super().__init__(f"RPC Error {self.code}: {self.message}")
