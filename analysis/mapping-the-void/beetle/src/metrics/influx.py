"""Tiny InfluxDB 1.x query helpers shared by the metric collectors."""

import json
import urllib.parse
import urllib.request

_DB = "geth"


def _query(endpoint: str, q: str) -> list[list]:
    """Rows for q, streamed in server-side chunks.

    A long replay reports for hours at 1s intervals; an unchunked query is
    silently cut at the server's max-row-limit (the `partial` flag is easy to
    miss), while chunked responses are exempt from it. Each chunk arrives as
    one JSON object per line; their rows concatenate in time order.
    """
    url = endpoint + "/query?" + urllib.parse.urlencode(
        {"db": _DB, "q": q, "chunked": "true", "chunk_size": "10000"}
    )
    rows: list[list] = []
    with urllib.request.urlopen(url, timeout=60) as r:
        for line in r:
            result = json.loads(line)["results"][0]
            if "error" in result:
                raise ValueError(f"influx: {result['error']} (query: {q})")
            for series in result.get("series", []):
                rows.extend(series["values"])
    return rows


def mean_ns(endpoint: str, measurement: str, host: str) -> float:
    """Event-weighted mean across the reporter intervals.

    A resetting timer reports one (count, mean) row per interval; averaging the
    means unweighted weights by wall-time and overstates slow warmup intervals.
    InfluxQL can't multiply fields inside an aggregate, so weight client-side.
    """
    rows = series(endpoint, measurement, host, '"count", "mean"')
    total = sum(r[1] for r in rows)
    if not total:
        return 0.0
    return sum(r[1] * r[2] for r in rows) / total


def series(endpoint: str, measurement: str, host: str, fields: str) -> list[list]:
    """Time-ordered raw points, one row per reporter interval."""
    q = (f'SELECT {fields} FROM "geth.{measurement}" '
         f"WHERE \"host\"='{host}' ORDER BY time ASC")
    return _query(endpoint, q)
