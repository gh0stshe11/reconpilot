"""Event system for ReconPilot"""
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4


class EventType(Enum):
    """Types of events in the system"""
    SCAN_STARTED = "scan_started"
    SCAN_COMPLETED = "scan_completed"
    SCAN_PAUSED = "scan_paused"
    SCAN_RESUMED = "scan_resumed"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_PROGRESS = "task_progress"
    ASSET_DISCOVERED = "asset_discovered"
    FINDING_DISCOVERED = "finding_discovered"
    LOG_MESSAGE = "log_message"


@dataclass
class Event:
    """Represents an event in the system"""
    type: EventType
    data: dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None


class EventBus:
    """Event bus for pub/sub pattern"""

    def __init__(self):
        self._subscribers: dict[EventType, list[Callable]] = {}
        self._history: list[Event] = []
        self._max_history = 1000

    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        """Subscribe to an event type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """Unsubscribe from an event type"""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)

    async def publish(self, event: Event) -> None:
        """Publish an event to all subscribers"""
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history.pop(0)

        if event.type in self._subscribers:
            for callback in self._subscribers[event.type]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)

    def get_history(
        self, event_type: Optional[EventType] = None, limit: Optional[int] = None
    ) -> list[Event]:
        """Get event history, optionally filtered by type"""
        history = self._history
        if event_type:
            history = [e for e in history if e.type == event_type]
        if limit:
            history = history[-limit:]
        return history

    def clear_history(self) -> None:
        """Clear event history"""
        self._history.clear()
