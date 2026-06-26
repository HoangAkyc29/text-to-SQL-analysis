"""Skill bundles: SKILL.md + TOOLS.md + prompts/ loaded for an agent.

A skill bundle is the composition of prompt management (item 7), the tool docs
that govern how tools (item 9) should be used, and the system-prompt fragments an
agent injects. It is how an agent learns *which* tools exist and *how* to use
them (the SKILL.md / TOOLS.md mechanism)."""

from agent_core.skills.bundle import SkillBundle

__all__ = ["SkillBundle"]
