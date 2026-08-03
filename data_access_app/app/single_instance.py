"""Ensure only one Data Access App process runs at a time.

Must be called before importing/starting Flet so a second launch never opens a window.
"""
from __future__ import annotations

import atexit
import os
import socket
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Resolve APP_ROOT without importing app.config (keeps this module light / early-safe)
from app.paths import app_root as _app_root_fn

_APP_ROOT = _app_root_fn()
_MUTEX_NAME = "Local\\MonorepoTradingAgent_DataAccessApp"
_LOCK_PATH = _APP_ROOT / "output" / ".data_access_app.lock"
_ERROR_ALREADY_EXISTS = 183

_holder: Any = None


@dataclass
class _ComboLock:
    """Windows mutex + exclusive lock file (both required)."""

    mutex_handle: int | None
    lock_fd: int | None
    lock_path: Path

    def release(self) -> None:
        if self.lock_fd is not None:
            try:
                if sys.platform == "win32":
                    import msvcrt

                    msvcrt.locking(self.lock_fd, msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
            except Exception:  # noqa: BLE001
                pass
            try:
                os.close(self.lock_fd)
            except Exception:  # noqa: BLE001
                pass
            self.lock_fd = None
        try:
            self.lock_path.unlink(missing_ok=True)
        except Exception:  # noqa: BLE001
            pass
        if self.mutex_handle:
            try:
                import ctypes

                ctypes.windll.kernel32.CloseHandle(self.mutex_handle)
            except Exception:  # noqa: BLE001
                pass
            self.mutex_handle = None


def port_is_listening(port: int, host: str = "127.0.0.1") -> bool:
    """True if something already accepts TCP on host:port (likely our live app)."""
    try:
        with socket.create_connection((host, int(port)), timeout=0.35):
            return True
    except OSError:
        return False


def _try_mutex() -> int | None:
    if sys.platform != "win32":
        return 0  # sentinel: no mutex needed
    import ctypes

    kernel32 = ctypes.windll.kernel32
    kernel32.SetLastError(0)
    handle = kernel32.CreateMutexW(None, False, _MUTEX_NAME)
    if not handle:
        return None
    err = int(kernel32.GetLastError())
    if err == _ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(handle)
        return None
    return int(handle)


def _try_file_lock() -> tuple[int, Path] | None:
    _LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(_LOCK_PATH), os.O_RDWR | os.O_CREAT, 0o644)
    try:
        if sys.platform == "win32":
            import msvcrt

            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        os.ftruncate(fd, 0)
        os.write(fd, f"{os.getpid()}\n".encode("ascii"))
        return fd, _LOCK_PATH
    except OSError:
        try:
            os.close(fd)
        except Exception:  # noqa: BLE001
            pass
        return None


def try_acquire() -> _ComboLock | None:
    """Acquire exclusive process lock, or None if another instance owns it."""
    mutex = _try_mutex()
    if mutex is None:
        return None
    file_part = _try_file_lock()
    if file_part is None:
        if mutex and sys.platform == "win32":
            import ctypes

            ctypes.windll.kernel32.CloseHandle(mutex)
        return None
    fd, path = file_part
    return _ComboLock(
        mutex_handle=mutex if sys.platform == "win32" else None,
        lock_fd=fd,
        lock_path=path,
    )


def show_already_running_modal(*, reason: str = "") -> None:
    title = "Ứng dụng đã mở"
    extra = f"\n\n({reason})" if reason else ""
    body = (
        "Data Access đang chạy.\n\n"
        "Chỉ được phép một cửa sổ. Dùng cửa sổ hiện có, hoặc đóng hẳn app rồi mở lại."
        f"{extra}"
    )
    print(f"DATA_ACCESS_ALREADY_RUNNING {reason}".strip(), flush=True)
    if sys.platform == "win32":
        try:
            import ctypes

            # MB_OK | MB_ICONWARNING | MB_SETFOREGROUND | MB_TOPMOST | MB_TASKMODAL
            ctypes.windll.user32.MessageBoxW(
                0,
                body,
                title,
                0x00000000 | 0x00000030 | 0x00010000 | 0x00040000 | 0x00002000,
            )
            return
        except Exception:  # noqa: BLE001
            pass
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showwarning(title, body, parent=root)
        root.destroy()
    except Exception:  # noqa: BLE001
        print(f"{title}: {body}", flush=True)


def acquire_or_exit(*, port: int | None = None) -> None:
    """
    Block a second process before Flet starts.

    Checks: (1) named mutex + lock file, (2) optional TCP port already listening.
    """
    global _holder
    if os.getenv("DATA_ACCESS_ALLOW_MULTI", "").strip().lower() in {"1", "true", "yes"}:
        return

    if port is not None and port_is_listening(int(port)):
        show_already_running_modal(reason=f"port {port} already in use")
        raise SystemExit(0)

    holder = try_acquire()
    if holder is None:
        show_already_running_modal(reason="another process holds the lock")
        raise SystemExit(0)

    # Port may become busy between check and bind — re-check after lock
    if port is not None and port_is_listening(int(port)):
        holder.release()
        show_already_running_modal(reason=f"port {port} already in use")
        raise SystemExit(0)

    _holder = holder

    def _cleanup() -> None:
        global _holder
        if _holder is not None:
            _holder.release()
            _holder = None

    atexit.register(_cleanup)
