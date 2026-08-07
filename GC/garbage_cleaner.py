import asyncio

from _logger import LOGGER


class GarbageCleaner:
    """Registry manager for tracking and safely canceling active asynchronous background garbage collection tasks."""

    def __init__(self):
        self._GARBAGE_COLLECTOR_TASKS: set[asyncio.Task] = set()

    async def start_gc(self):
        """Start the background asynchronous garbage collector task for cleanups."""
        LOGGER.debug("Garbage cleaner started")

    def register_task(self, t: asyncio.Task):
        """Register a background task to prevent garbage collection and auto-remove it upon completion.

        Args:
            t: The active asyncio Task instance to be tracked.
        """
        self._GARBAGE_COLLECTOR_TASKS.add(t)
        t.add_done_callback(self._GARBAGE_COLLECTOR_TASKS.discard)
        LOGGER.debug("GC task registered")

    async def close_gc(self):
        """Cancel and stop all active background garbage collector tasks safely."""
        LOGGER.debug("Stopping garbage collector")
        for t in self._GARBAGE_COLLECTOR_TASKS:
            t.cancel()
