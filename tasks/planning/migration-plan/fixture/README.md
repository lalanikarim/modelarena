# Data Pipeline App

A small async data pipeline that fetches from multiple URLs and transforms results.

## Current state
- Python 3.9 target
- Uses `typing.Dict`, `typing.List`, `typing.Optional` throughout
- Uses `asyncio.get_event_loop()` in main()
- Depends on aiohttp 3.8.x and pydantic v1

## Known issues
- `asyncio.get_event_loop()` emits DeprecationWarning on 3.10+
- pydantic v1 is EOL; v2 has breaking changes
- No type checking configured (mypy not in CI)
