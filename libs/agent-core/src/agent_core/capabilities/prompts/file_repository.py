"""Concrete prompt management (item 7): load prompts from Markdown files.

Each prompt file may carry YAML frontmatter for versioning + few-shots:

    ---
    version: "1.2.0"
    few_shots:
      - input: "..."
        output: "..."
    ---
    The actual prompt body with {variables}.

Bodies are rendered with the existing :class:`StringPromptTemplate`.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from agent_core.capabilities.prompts.base import (
    PromptRepository,
    PromptTemplate,
    PromptVersion,
    StringPromptTemplate,
)


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            header = text[3:end].strip()
            body = text[end + 4 :].lstrip("\n")
            return (yaml.safe_load(header) or {}), body
    return {}, text


class FilePromptRepository(PromptRepository):
    """Load prompt versions from a directory of ``*.md`` files."""

    def __init__(self, prompts_dir: Path) -> None:
        self.prompts_dir = Path(prompts_dir)
        self._cache: dict[str, PromptVersion] = {}

    def _load_file(self, name: str) -> PromptVersion:
        path = self.prompts_dir / f"{name}.md"
        if not path.exists():
            raise FileNotFoundError(f"Prompt '{name}' not found at {path}")
        meta, body = _parse_frontmatter(path.read_text(encoding="utf-8"))
        return PromptVersion(
            version=str(meta.get("version", "1.0.0")),
            template=body,
            few_shots=list(meta.get("few_shots", [])),
            metadata={k: v for k, v in meta.items() if k not in ("version", "few_shots")},
        )

    def get(self, name: str, version: str | None = None) -> PromptVersion:
        if name not in self._cache:
            self._cache[name] = self._load_file(name)
        return self._cache[name]

    def register(self, name: str, version: PromptVersion) -> None:
        self._cache[name] = version

    def template(self, name: str) -> PromptTemplate:
        """Convenience: get a renderable template for ``name``."""
        return StringPromptTemplate(self.get(name))

    def text(self, name: str) -> str:
        """Return the raw prompt body (no rendering)."""
        return self.get(name).template
