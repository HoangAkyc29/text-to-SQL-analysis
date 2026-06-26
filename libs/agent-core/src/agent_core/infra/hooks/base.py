"""Item 35 - Hooks / Middleware / Callbacks.

Cross-cutting extension points around the agent lifecycle:
``on_start`` / ``before_step`` / ``after_step`` / ``on_end``. Mirrors the Strands
hook system so concrete hooks can also register with a Strands agent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LifecycleEvent(str, Enum):
    ON_START = "on_start"
    BEFORE_STEP = "before_step"
    AFTER_STEP = "after_step"
    ON_END = "on_end"
    ON_ERROR = "on_error"


@dataclass(slots=True)
class HookContext:
    """Mutable context passed to hooks."""

    event: LifecycleEvent
    data: dict[str, Any] = field(default_factory=dict)


class Hook:
    """Base hook: override the lifecycle methods you care about."""

    def on_start(self, ctx: HookContext) -> None: ...
    def before_step(self, ctx: HookContext) -> None: ...
    def after_step(self, ctx: HookContext) -> None: ...
    def on_end(self, ctx: HookContext) -> None: ...
    def on_error(self, ctx: HookContext) -> None: ...


class HookManager:
    """Dispatch lifecycle events to registered hooks."""

    def __init__(self, hooks: list[Hook] | None = None) -> None:
        self._hooks = list(hooks or [])

    def add(self, hook: Hook) -> None:
        self._hooks.append(hook)

    def emit(self, event: LifecycleEvent, **data: Any) -> HookContext:
        ctx = HookContext(event=event, data=data)
        for hook in self._hooks:
            getattr(hook, event.value)(ctx)
        return ctx
