"""agent-core: abstract building blocks for Strands-based agents (items 1-36).

Importing this package is cheap: it only exposes sub-packages, each of which
contains a ``base.py`` with the abstraction for one concept.
"""

__all__ = [
    "core",
    "capabilities",
    "state",
    "tasks",
    "multiagent",
    "infra",
]
