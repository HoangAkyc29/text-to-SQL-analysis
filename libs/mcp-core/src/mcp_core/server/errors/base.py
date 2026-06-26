"""Item 47 - Error handling.

Map domain exceptions to JSON-RPC error objects so clients get consistent,
machine-readable errors.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

# Standard JSON-RPC error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


@dataclass(slots=True)
class JsonRpcError:
    """A JSON-RPC error payload."""

    code: int
    message: str
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "data": self.data}


class MCPErrorMapper(ABC):
    """Translate a domain exception into a :class:`JsonRpcError`."""

    @abstractmethod
    def map(self, exc: BaseException) -> JsonRpcError: ...


class DefaultErrorMapper(MCPErrorMapper):
    """Maps everything to INTERNAL_ERROR, preserving the message."""

    def map(self, exc: BaseException) -> JsonRpcError:
        code = getattr(exc, "code", None)
        return JsonRpcError(
            code=INVALID_PARAMS if isinstance(exc, (ValueError, KeyError)) else INTERNAL_ERROR,
            message=str(exc),
            data={"type": type(exc).__name__, "domain_code": code},
        )
