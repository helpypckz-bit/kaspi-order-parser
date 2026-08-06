from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

T = TypeVar("T")


def deep_get(data: Mapping[str, Any] | None, path: str, default: T) -> Any | T:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, Mapping):
            return default
        current = current.get(part)
        if current is None:
            return default
    return current


def safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
