import functools
import os
from pathlib import Path


@functools.cache
def _load() -> None:
    env = Path(".env")
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, _, value = stripped.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def require(name: str) -> str:
    _load()
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"missing required env var {name!r} (set it in .env)")
    return value
