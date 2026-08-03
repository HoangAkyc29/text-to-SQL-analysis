"""Classify ODBC / SQL failures into stable, user-facing DbError messages."""
from __future__ import annotations


class DbError(RuntimeError):
    """User-facing database failure (Vietnamese message preferred)."""


# Substrings / SQLSTATE fragments seen when SQL Server is down, restoring, or timing out.
_RESTORE_HINTS = (
    "restoring",
    "recovery",
    "recovering",
    "database is in",
    "suspect",
    "emergency mode",
    "single_user",
    "cannot open database",
    "unable to open the physical file",
    "offline",
)
_DISCONNECT_HINTS = (
    "communication link failure",
    "tcp provider",
    "connection is busy",
    "connection was forcibly closed",
    "connection reset",
    "broken pipe",
    "not connected",
    "connection failed",
    "unable to complete login",
    "login timeout",
    "server is not found",
    "could not open a connection",
    "named pipes provider",
    "network path was not found",
    "error locating server",
    "actively refused",
    "timeout expired",
    "semaphore timeout",
    "hy000",
    "08s01",
    "08001",
    "hyt00",
    "hyt01",
    "im002",  # DSN not found
)
_TIMEOUT_HINTS = (
    "timeout",
    "timed out",
    "hyt00",
    "hyt01",
    "query timeout",
)
_PERMISSION_HINTS = (
    "login failed",
    "permission denied",
    "not authorized",
    "18456",
)


def _exc_blob(exc: BaseException) -> str:
    parts: list[str] = [str(exc)]
    args = getattr(exc, "args", ()) or ()
    for a in args:
        parts.append(str(a))
    cause = getattr(exc, "__cause__", None)
    if cause is not None:
        parts.append(str(cause))
    return " | ".join(parts).lower()


def classify_db_failure(exc: BaseException, *, target: str | None = None) -> str:
    """
    Return a short Vietnamese message for UI / DbError.
    Does not include stack traces.
    """
    blob = _exc_blob(exc)
    where = f" ({target})" if target else ""

    if any(h in blob for h in _RESTORE_HINTS):
        return (
            f"Cơ sở dữ liệu{where} đang restore / recovery / offline. "
            "Đợi SQL Server xong rồi thử lại (Settings → Test db)."
        )
    if any(h in blob for h in _TIMEOUT_HINTS) and "login" not in blob:
        return (
            f"Hết thời gian chờ truy vấn{where}. "
            "DB có thể đang chậm hoặc mất kết nối — thử lại sau."
        )
    if any(h in blob for h in _DISCONNECT_HINTS):
        return (
            f"Mất kết nối SQL Server{where}. "
            "Kiểm tra mạng / instance đang chạy / DSN trong Settings."
        )
    if any(h in blob for h in _PERMISSION_HINTS):
        return (
            f"Đăng nhập SQL thất bại{where}. "
            "Kiểm tra tài khoản trong chuỗi DSN (.env)."
        )
    raw = str(exc).strip()
    if raw.startswith(("Không ", "Cơ sở ", "Mất ", "Hết ", "Đăng nhập ")):
        return raw
    if len(raw) > 220:
        raw = raw[:217] + "…"
    return f"Lỗi SQL{where}: {raw}"


def wrap_db_exception(exc: BaseException, *, target: str | None = None) -> DbError:
    if isinstance(exc, DbError):
        return exc
    return DbError(classify_db_failure(exc, target=target))


def is_missing_object_error(exc: BaseException) -> bool:
    msg = _exc_blob(exc)
    return (
        "invalid object name" in msg
        or "does not exist" in msg
        or "invalid object" in msg
        or ("42s02" in msg)
    )


def user_facing_error(exc: BaseException | str | None) -> str:
    """Normalize anything thrown from a job into one status-bar line."""
    if exc is None:
        return "Lỗi không xác định"
    if isinstance(exc, str):
        first = exc.split("\n", 1)[0].strip()
        return first or "Lỗi không xác định"
    if isinstance(exc, DbError):
        return str(exc)
    if isinstance(exc, ValueError):
        return str(exc)
    return classify_db_failure(exc)
