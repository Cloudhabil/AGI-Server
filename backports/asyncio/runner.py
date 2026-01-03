"""Simplified asyncio.Runner backport for Python <3.11."""
from __future__ import annotations

import asyncio
from typing import Any, Coroutine, Optional, Type


class Runner:
    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

    def run(self, coro: Coroutine[Any, Any, Any]) -> Any:
        return self._loop.run_until_complete(coro)

    def close(self) -> None:
        self._loop.close()
        asyncio.set_event_loop(None)

    def __enter__(self) -> "Runner":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[Any],
    ) -> None:
        self.close()
