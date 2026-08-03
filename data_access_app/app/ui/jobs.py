"""Background job runner for Flet — UI callbacks on page thread."""
from __future__ import annotations

import sys
import traceback
from dataclasses import dataclass
from typing import Any, Callable

from app.db.errors import user_facing_error


@dataclass
class JobState:
    running: bool = False
    cancelled: bool = False
    message: str = ""
    error: str = ""  # short, user-facing (status bar)
    error_detail: str = ""  # full traceback (logs only)
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
                self.state.error = user_facing_error(exc)
                self.state.error_detail = traceback.format_exc()
                self.state.message = "Lỗi"
                print(
                    f"DATA_ACCESS_JOB_ERROR: {self.state.error}\n{self.state.error_detail}",
                    file=sys.stderr,
                    flush=True,
                )
            finally:
                self.state.running = False
                self._lock_running = False

                def _finish() -> None:
                    try:
                        if on_done:
                            on_done(self.state)
                    except Exception as ui_exc:  # noqa: BLE001
                        # Never let a UI callback crash the worker/session thread.
                        print(
                            f"DATA_ACCESS_UI_CALLBACK_ERROR: {ui_exc}\n{traceback.format_exc()}",
                            file=sys.stderr,
                            flush=True,
                        )

                if pg is not None and hasattr(pg, "run_thread"):
                    try:
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
