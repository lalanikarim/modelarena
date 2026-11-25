"""Utility functions. Targets Python 3.9."""
import json
from typing import Any, Dict, List


# Uses collections.namedtuple — fine but dataclasses are preferred in 3.12
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])


async def fetch_data(url: str) -> Dict[str, Any]:
    """Simulate fetching data (placeholder for aiohttp/requests)."""
    # In production this would be an HTTP call
    return {"url": url, "data": [1, 2, 3]}


def transform(data: Dict[str, Any]) -> str:
    """Transform raw data into a display string."""
    items = data.get("data", [])
    # Uses the old-style list comprehension with explicit type hint
    total: int = sum(items)  # type annotation on local var (unnecessary in 3.12)
    return f"{data['url']}: {total}"


# Uses typing.Dict and typing.List instead of built-in dict/list
def batch_process(urls: List[str]) -> Dict[str, List[int]]:
    results: Dict[str, List[int]] = {}
    for url in urls:
        results[url] = [1, 2, 3]  # placeholder
    return results
