"""Load a skill bundle from disk: SKILL.md + TOOLS.md + prompts/*.md.

Directory layout (per agent):

    skills/<skill_name>/
        SKILL.md            # overview, budgets, when to read what
        TOOLS.md            # canonical tool list, prefixes, params, examples
        prompts/
            system_base.md  # base system prompt
            <guide>.md      # task-specific guides

The bundle turns these into system-prompt fragments + a tool-usage guide that the
context builder (item 8) injects, so the agent actually follows the documented
tool rules instead of guessing.
"""

from __future__ import annotations

from pathlib import Path

from agent_core.capabilities.prompts.file_repository import FilePromptRepository


class SkillBundle:
    """In-memory view of a skill's docs + prompts."""

    def __init__(self, name: str, root: Path) -> None:
        self.name = name
        self.root = Path(root)
        self.skill_md = self._read("SKILL.md")
        self.tools_md = self._read("TOOLS.md")
        prompts_dir = self.root / "prompts"
        self.prompts = FilePromptRepository(prompts_dir) if prompts_dir.exists() else None

    def _read(self, filename: str) -> str:
        path = self.root / filename
        return path.read_text(encoding="utf-8") if path.exists() else ""

    @classmethod
    def load(cls, skills_root: Path, name: str) -> "SkillBundle":
        return cls(name, Path(skills_root) / name)

    def system_prompt(self) -> str:
        """Base system prompt for this skill (prompts/system_base.md if present)."""
        if self.prompts is not None:
            try:
                return self.prompts.text("system_base")
            except FileNotFoundError:
                pass
        return self.skill_md

    def guide(self, name: str) -> str:
        """Return a task guide body by name (prompts/<name>.md)."""
        if self.prompts is None:
            return ""
        try:
            return self.prompts.text(name)
        except FileNotFoundError:
            return ""

    def tool_docs(self) -> str:
        """The tool-usage guide injected into context (TOOLS.md)."""
        return self.tools_md

    def system_fragments(self) -> list[str]:
        """All fragments to prepend to the agent's system prompt."""
        frags = [self.system_prompt()]
        if self.skill_md and self.skill_md not in frags:
            frags.append(self.skill_md)
        return [f for f in frags if f.strip()]
