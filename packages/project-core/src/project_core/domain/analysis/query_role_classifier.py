from __future__ import annotations

from typing import Literal

QueryRoleMode = Literal[
    "normal",
    "probe_only",
    "probe_only_success",
    "main_empty_probe_hit",
    "all_empty",
]


def classify_query_roles(
    meta: list[dict],
    row_counts: dict[int, int],
    *,
    num_queries: int | None = None,
) -> tuple[QueryRoleMode, int, int, list[int], list[int]]:
    """Classify main vs probe row counts without treating all-probe plans as main."""
    n = num_queries
    if n is None:
        keys = list(row_counts.keys())
        n = max(len(meta), max(keys) + 1 if keys else 0)

    probe_idxs = [i for i, m in enumerate(meta) if m.get("role") == "probe"]
    explicit_main_idxs = [i for i, m in enumerate(meta) if m.get("role") != "probe"]

    if probe_idxs and not explicit_main_idxs:
        probe_rows = sum(row_counts.get(i, 0) for i in probe_idxs)
        mode: QueryRoleMode = "probe_only_success" if probe_rows > 0 else "probe_only"
        return mode, 0, probe_rows, [], probe_idxs

    main_idxs = explicit_main_idxs if explicit_main_idxs else [i for i in range(n) if i not in probe_idxs]
    if not main_idxs:
        main_idxs = list(range(n))

    main_rows = sum(row_counts.get(i, 0) for i in main_idxs)
    probe_rows = sum(row_counts.get(i, 0) for i in probe_idxs)

    if main_rows == 0 and probe_rows > 0:
        mode = "main_empty_probe_hit"
    elif main_rows == 0:
        mode = "all_empty"
    else:
        mode = "normal"
    return mode, main_rows, probe_rows, main_idxs, probe_idxs
