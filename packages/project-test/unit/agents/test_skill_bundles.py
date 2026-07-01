"""Verify supermarket agent skill bundles load from disk."""

from __future__ import annotations

from pathlib import Path

import pytest
from agent_core.skills.bundle import SkillBundle

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[4]


@pytest.mark.parametrize(
    ("agent_pkg", "skill_name"),
    [
        ("conversational-router/src/conversational_router", "router"),
        ("sql-planner/src/sql_planner", "sql_planner"),
        ("risk-reviewer/src/risk_reviewer", "risk_reviewer"),
        ("data-analyst/src/data_analyst", "analyst"),
    ],
)
def test_skill_bundle_loads(agent_pkg: str, skill_name: str):
    skills_root = ROOT / "agents" / agent_pkg / "skills"
    bundle = SkillBundle.load(skills_root, skill_name)
    assert bundle.skill_md.strip(), f"SKILL.md missing for {skill_name}"
    assert bundle.tools_md.strip(), f"TOOLS.md missing for {skill_name}"
    assert bundle.system_prompt().strip(), f"system_base.md missing for {skill_name}"


def test_router_guides_exist():
    skills_root = ROOT / "agents" / "conversational-router" / "src" / "conversational_router" / "skills"
    bundle = SkillBundle.load(skills_root, "router")
    for guide in ("ingress_guide", "clarification_bridge_guide", "clarify_guide", "synthesize_guide"):
        assert bundle.guide(guide).strip(), f"missing {guide}"


def test_sql_planner_guides_exist():
    skills_root = ROOT / "agents" / "sql-planner" / "src" / "sql_planner" / "skills"
    bundle = SkillBundle.load(skills_root, "sql_planner")
    assert bundle.guide("plan_sql_guide").strip()
    assert bundle.guide("probe_feedback_guide").strip()


def test_ingress_prompt_assembles():
    skills_root = ROOT / "agents" / "conversational-router" / "src" / "conversational_router" / "skills"
    bundle = SkillBundle.load(skills_root, "router")
    parts = bundle.system_fragments() + [bundle.guide("ingress_guide")]
    prompt = "\n\n---\n\n".join(p for p in parts if p.strip())
    assert "Agent I" in prompt or "Conversational Router" in prompt
    assert "route" in prompt.lower()
