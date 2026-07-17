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
