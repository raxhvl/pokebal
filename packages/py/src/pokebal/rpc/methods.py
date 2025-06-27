from pydantic import TypeAdapter
from .client import RPCClient
from .types import BlockDebugTraceResult


class EthereumMethods:
    def __init__(self, client: RPCClient):
        self.client = client

    def get_block_number(self) -> int:
        result = self.client.call("eth_blockNumber")
        return int(result, 16)

    def get_balance(self, address: str, block: str = "latest") -> int:
        result = self.client.call("eth_getBalance", [address, block])
        return int(result, 16)

    def debug_traceBlockByNumber(
        self, block_number: int, diff_mode: bool = True
    ) -> BlockDebugTraceResult:
        result = self.client.call(
            "debug_traceBlockByNumber",
            [
                hex(block_number),
                {"tracer": "prestateTracer", "tracerConfig": {"diffMode": diff_mode}},
            ],
        )
        adapter = TypeAdapter(BlockDebugTraceResult)
        return adapter.validate_python(result)
