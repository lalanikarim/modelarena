"""Main application entry point. Targets Python 3.9."""
import asyncio
from typing import Dict, List, Optional  # BUG: should use built-in dict/list in 3.12+

from utils import fetch_data, transform


# Uses the old-style loop variable annotation (fine but outdated)
async def process_items(items: List[Dict]) -> List[str]:
    results: List[str] = []
    for item in items:  # type: Dict
        data = await fetch_data(item["url"])
        results.append(transform(data))
    return results


# Uses asyncio.get_event_loop() — deprecated in 3.10+, removed pattern in 3.12
async def main():
    loop = asyncio.get_event_loop()  # DEPRECATED: use asyncio.run() or get_running_loop()
    items = [
        {"url": "http://api.example.com/users"},
        {"url": "http://api.example.com/posts"},
    ]
    results = await process_items(items)
    for r in results:
        print(r)


# Uses the old typing.Optional instead of X | None
def parse_config(raw: Optional[str]) -> Dict:
    if raw is None:
        return {}
    import json
    return json.loads(raw)


if __name__ == "__main__":
    # asyncio.run() is correct, but main() internally uses get_event_loop()
    asyncio.run(main())
