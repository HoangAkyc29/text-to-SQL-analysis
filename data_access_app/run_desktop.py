"""Desktop entrypoint for PyInstaller / flet pack (always native window)."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def _configure_frozen_runtime() -> None:
    # Avoid UnicodeEncodeError on Windows cp1252 consoles.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:
            pass

    os.environ.setdefault("DATA_ACCESS_FLET_VIEW", "desktop")
    os.environ.setdefault("DATA_ACCESS_PORT", "13059")
    os.environ.setdefault("PYTHONUTF8", "1")
    if not getattr(sys, "frozen", False):
        return
    # Bundled Flet desktop client (avoids first-run GitHub download / SSL issues).
    if os.environ.get("FLET_VIEW_PATH"):
        return
    exe_dir = Path(sys.executable).resolve().parent
    candidates = [
        exe_dir / "flet_view",
        exe_dir / "_internal" / "flet_view",
    ]
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(meipass) / "flet_view")
    for cand in candidates:
        if (cand / "flet.exe").is_file():
            os.environ["FLET_VIEW_PATH"] = str(cand)
            print(f"DATA_ACCESS_FLET_VIEW_PATH={cand}", flush=True)
            return


_configure_frozen_runtime()

from app.main import _run

if __name__ == "__main__":
    _run()
