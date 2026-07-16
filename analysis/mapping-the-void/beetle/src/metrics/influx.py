"""Tiny InfluxDB 1.x query helpers shared by the metric collectors."""

import json
import urllib.parse
import urllib.request

_DB = "geth"


def _query(endpoint: str, q: str) -> list[list]:
    url = endpoint + "/query?" + urllib.parse.urlencode({"db": _DB, "q": q})
    with urllib.request.urlopen(url, timeout=15) as r:
        series = json.load(r)["results"][0].get("series")
    return series[0]["values"] if series else []


def mean_ns(endpoint: str, measurement: str, host: str) -> float:
    q = f'SELECT mean("mean") FROM "geth.{measurement}" WHERE "host"=\'{host}\''
    values = _query(endpoint, q)
    return values[0][1] if values else 0.0


def series(endpoint: str, measurement: str, host: str, fields: str) -> list[list]:
    """Time-ordered raw points, one row per reporter interval."""
    q = (f'SELECT {fields} FROM "geth.{measurement}" '
         f"WHERE \"host\"='{host}' ORDER BY time ASC")
    return _query(endpoint, q)
