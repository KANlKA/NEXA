#async pub-sub system.

import asyncio
from collections import defaultdict
from typing import Callable, Awaitable, Any

class EventBus:
    def __init__(self):
        # Maps an event name -> list of functions to call when it fires
        self._subscribers: dict[str, list[Callable[..., Awaitable[None]]]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: Callable[..., Awaitable[None]]) -> None:
        """Register a handler to run whenever `event_name` is published."""
        self._subscribers[event_name].append(handler)

    async def publish(self, event_name: str, payload: Any = None) -> None:
        """
        Fire an event. All subscribed handlers run concurrently
        (not one-by-one) so a slow handler doesn't block the others.
        """
        handlers = self._subscribers.get(event_name, [])
        if not handlers:
            return
        await asyncio.gather(*(handler(payload) for handler in handlers))

# Singleton
_bus_instance = None


def get_event_bus() -> EventBus:
    global _bus_instance
    if _bus_instance is None:
        _bus_instance = EventBus()
    return _bus_instance
