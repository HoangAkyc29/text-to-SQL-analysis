from __future__ import annotations

import os


def enable_llm_stub() -> None:
    os.environ["ALLOW_LLM_STUB"] = "1"
