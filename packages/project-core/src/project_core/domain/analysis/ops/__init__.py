"""Agent IV analysis ops — parameterized tools over parquet working sets.

No LLM-authored scripts. Ops run in-process with pandas and write artifacts
under the trace ``out/`` directory.
"""

from __future__ import annotations

from project_core.domain.analysis.ops.registry import (
    OP_CATALOG,
    OpResult,
    execute_op,
    list_op_ids,
)
from project_core.domain.analysis.ops.working_set import DatasetHandle, DatasetWorkingSet

__all__ = [
    "DatasetHandle",
    "DatasetWorkingSet",
    "OP_CATALOG",
    "OpResult",
    "execute_op",
    "list_op_ids",
]
