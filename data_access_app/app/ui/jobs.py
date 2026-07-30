"""Background job runner for Flet — UI callbacks on page thread."""
from __future__ import annotations

import traceback
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class JobState:
    running: bool = False
    cancelled: bool = False
    message: str = ""
    error: str = ""
    result: Any = None


class JobRunner:
    def __init__(self, page=None) -> None:
        self.page = page
        self.state = JobState()
        self._lock_running = False

    def cancel(self) -> None:
        self.state.cancelled = True
        self.state.message = "Đang hủy…"

    def is_cancelled(self) -> bool:
        return self.state.cancelled

    def set_message(self, msg: str) -> None:
        self.state.message = msg

    def run(
        self,
        fn: Callable[[], Any],
        *,
        on_done: Callable[[JobState], None] | None = None,
        page=None,
    ) -> bool:
        if self.state.running or self._lock_running:
            return False
        self._lock_running = True
        self.state = JobState(running=True, message="Đang chạy…")
        pg = page or self.page

        def _wrap() -> None:
            try:
                self.state.result = fn()
                self.state.message = "Hoàn tất"
            except Exception as exc:  # noqa: BLE001
                self.state.error = f"{exc}\n{traceback.format_exc()}"
                self.state.message = "Lỗi"
            finally:
                self.state.running = False
                self._lock_running = False

                def _finish() -> None:
                    if on_done:
                        on_done(self.state)

                # Prefer UI-thread finish when page is available
                if pg is not None and hasattr(pg, "run_thread"):
                    # on_done must touch controls on the session thread;
                    # schedule via a no-op run_task pattern when possible.
                    try:
                        import asyncio

                        async def _async_finish():
                            _finish()

                        pg.run_task(_async_finish)
                        return
                    except Exception:  # noqa: BLE001
                        pass
                _finish()

        if pg is not None and hasattr(pg, "run_thread"):
            pg.run_thread(_wrap)
        else:
            import threading

            threading.Thread(target=_wrap, daemon=True).start()
        return True
