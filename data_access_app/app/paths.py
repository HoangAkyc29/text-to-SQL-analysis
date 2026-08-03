"""Resolve app install root for both source and frozen (PyInstaller) runs."""
from __future__ import annotations

import sys
from pathlib import Path


def app_root() -> Path:
    """Directory that holds `.env`, `output/`, and the executable (when frozen)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))
