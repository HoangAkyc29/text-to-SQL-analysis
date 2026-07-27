from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from project_core.domain.contracts.brief import AnalysisBrief, TimeRange


class DecisionLogEntry(BaseModel):
    what: str
    why: str = ""


class WorkingMemory(BaseModel):
    """Bounded CCS (L2) — ground truth for multi-turn follow-ups."""

    current_goal: str = ""
    active_constraints: list[str] = Field(default_factory=list)
    key_facts: list[str] = Field(default_factory=list)
    decision_log: list[DecisionLogEntry] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    active_filters: dict[str, Any] = Field(default_factory=dict)
    active_time_range: TimeRange = Field(default_factory=TimeRange)
    output_format: list[str] = Field(default_factory=list)

    def capped(
        self,
        *,
        max_constraints: int = 10,
        max_facts: int = 20,
        max_decisions: int = 15,
        max_questions: int = 5,
    ) -> WorkingMemory:
        return self.model_copy(
            update={
                "active_constraints": list(self.active_constraints)[:max_constraints],
                "key_facts": list(self.key_facts)[:max_facts],
                "decision_log": list(self.decision_log)[-max_decisions:],
                "open_questions": list(self.open_questions)[:max_questions],
            }
        )


class CompactArchiveEntry(BaseModel):
    """One compressed snapshot (L3)."""

    at: str
    reason: str = "curator"
    summary: str = ""
    selected_turn_ids: list[str] = Field(default_factory=list)
    observations: list[str] = Field(default_factory=list)
    source_turn_ids: list[str] = Field(default_factory=list)


class SelectedTurn(BaseModel):
    id: str
    role: str
    content_trimmed: str
    why_selected: str = "recency"
    kind: str = "chat"


class ContextPackMeta(BaseModel):
    token_est: int = 0
    budget: int = 3500
    pct: float = 0.0
    dropped_turns: int = 0
    noise_ratio_est: float = 0.0
    strategy: str = "hard_only"
    curator_invoked: bool = False
    curator_failed: bool = False
    archive_id: str | None = None
    pct_before: float | None = None
    pct_after: float | None = None
    # ISO calendar date of this conversation turn (YYYY-MM-DD).
    as_of_date: str | None = None


class ContextPack(BaseModel):
    """Assembled payload for Agent I ingress / clarification bridge (never full L0)."""

    working_memory: WorkingMemory = Field(default_factory=WorkingMemory)
    last_resolved_brief: AnalysisBrief | None = None
    selected_turns: list[SelectedTurn] = Field(default_factory=list)
    compact_notes: list[CompactArchiveEntry] = Field(default_factory=list)
    current_message: str = ""
    sticky_rules: list[str] = Field(default_factory=list)
    pack_meta: ContextPackMeta = Field(default_factory=ContextPackMeta)
    external_sources: list[dict[str, Any]] = Field(default_factory=list)

    def to_ingress_user_content(self) -> dict[str, Any]:
        """Positional-ish JSON: CCS/prior/sticky/current near the end for attention."""
        return {
            "selected_turns": [t.model_dump(mode="json") for t in self.selected_turns],
            "compact_notes": [n.model_dump(mode="json") for n in self.compact_notes],
            "working_memory": self.working_memory.model_dump(mode="json"),
            "last_resolved_brief": (
                self.last_resolved_brief.model_dump(mode="json")
                if self.last_resolved_brief
                else None
            ),
            "sticky_rules": list(self.sticky_rules),
            "current_message": self.current_message,
            "external_sources": list(self.external_sources),
            "pack_meta": self.pack_meta.model_dump(mode="json"),
        }


STICKY_RULES_DEFAULT: tuple[str, ...] = (
    "Brief for analysis must be self-contained: never leave anaphora like 'tương tự', 'như trên', 'trước đó' unresolved.",
    "On follow_up/revise, merge last_resolved_brief / working_memory with the current delta; rewrite intent fully.",
    "Mark carried fields with requirements.source=carried; only quote current_message for source=explicit.",
    "Never invent SQL or domain TRANS_CODE recipes.",
)
