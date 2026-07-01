from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from project_core.domain.feedback.analysis_tool_registry import AnalysisToolRegistry

_registry: AnalysisToolRegistry | None = None


def set_registry(registry: AnalysisToolRegistry | None) -> None:
    global _registry
    _registry = registry


def get_registry() -> AnalysisToolRegistry | None:
    return _registry
