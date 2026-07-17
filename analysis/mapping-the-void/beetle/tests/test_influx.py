"""The chunked-query helper against a stub InfluxDB endpoint."""

import http.server
import json
import threading

import pytest

from metrics import influx


class _Stub(http.server.BaseHTTPRequestHandler):
    body: bytes = b""

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(self.body)

    def log_message(self, *args):
        pass


@pytest.fixture
def endpoint():
    server = http.server.HTTPServer(("127.0.0.1", 0), _Stub)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


def _chunks(*value_batches) -> bytes:
    lines = [
        json.dumps({"results": [{"series": [{"name": "s", "values": list(batch)}]}]})
        for batch in value_batches
    ]
    return ("\n".join(lines) + "\n").encode()


def test_series_concatenates_chunks(endpoint):
    _Stub.body = _chunks([[1, 10], [2, 20]], [[3, 30]])
    rows = influx.series(endpoint, "m.timer", "BAL-base", '"count"')
    assert rows == [[1, 10], [2, 20], [3, 30]]


def test_query_error_raises_instead_of_empty_charts(endpoint):
    _Stub.body = json.dumps({"results": [{"error": "database not found"}]}).encode()
    with pytest.raises(ValueError, match="database not found"):
        influx.series(endpoint, "m.timer", "BAL-base", '"count"')


def test_mean_ns_weights_by_event_count(endpoint):
    # (time, count, mean): 2 events at 10ns, 8 at 20ns -> 18ns overall
    _Stub.body = _chunks([[0, 2, 10.0]], [[1, 8, 20.0]])
    assert influx.mean_ns(endpoint, "m.timer", "BAL-base") == pytest.approx(18.0)
