"""Item 36 - Config / Dependency injection.

A tiny service container to wire concrete implementations of the abstractions
together and swap them via config. Keeps construction in one place so an agent
app is assembled declaratively.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")

Provider = Callable[["Container"], Any]


class Container:
    """Minimal DI container with singletons and factories.

    - ``register`` a factory under a key.
    - ``singleton`` caches the first resolution.
    - ``resolve`` builds (or returns the cached) instance, injecting the
      container so providers can resolve their own dependencies.
    """

    def __init__(self) -> None:
        self._providers: dict[str, Provider] = {}
        self._singletons: dict[str, bool] = {}
        self._cache: dict[str, Any] = {}

    def register(self, key: str, provider: Provider, *, singleton: bool = True) -> None:
        self._providers[key] = provider
        self._singletons[key] = singleton

    def instance(self, key: str, value: Any) -> None:
        """Register an already-built instance."""
        self._cache[key] = value
        self._providers[key] = lambda _c: value
        self._singletons[key] = True

    def resolve(self, key: str) -> Any:
        if key in self._cache:
            return self._cache[key]
        if key not in self._providers:
            raise KeyError(f"No provider registered for '{key}'")
        value = self._providers[key](self)
        if self._singletons.get(key, True):
            self._cache[key] = value
        return value

    def has(self, key: str) -> bool:
        return key in self._providers
