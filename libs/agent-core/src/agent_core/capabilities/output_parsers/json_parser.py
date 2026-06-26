"""Concrete output parser (item 11): extract a JSON object from model text."""

from __future__ import annotations

import json
from typing import Any

from agent_core.capabilities.output_parsers.base import OutputParser, ParseResult


class JSONOutputParser(OutputParser[dict]):
    """Find and parse the first/last balanced JSON object in the text."""

    def parse(self, text: str) -> ParseResult[dict]:
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            data: dict[str, Any] = json.loads(text[start:end])
            return ParseResult(ok=True, value=data, raw=text)
        except (ValueError, json.JSONDecodeError) as exc:
            return ParseResult(ok=False, error=str(exc), raw=text)
