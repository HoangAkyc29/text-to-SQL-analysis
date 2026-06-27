from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from project_core.paths import ROOT


class PipelineConfig(BaseModel):
    max_sql_queries_per_plan: int = 6
    max_sql_retries: int = 3
    max_risk_retries: int = 2
    max_clarify_rounds: int = 3
    max_sync_seconds: int = 120
    iv_max_steps: int = 8
    poll_enabled: bool = True
    workflow_stale_ttl_seconds: int = 900
    workflow_steps_max: int = 200
    workflow_steps_scope: str = "analysis"


class ClarificationConfig(BaseModel):
    hard_enforce: bool = True
    bridge_min_confidence: float = 0.75


class RagConfig(BaseModel):
    clarify_min_score: float = 0.72
    top_k: int = 5


class BudgetConfig(BaseModel):
    agent_caps: dict[str, int] = Field(default_factory=dict)
    max_tokens_per_trace: int = 200_000


class PolicyConfig(BaseModel):
    max_rows: int = 50_000
    max_join_depth: int = 5
    default_schema: str = "dbo"


class ArtifactsConfig(BaseModel):
    base_dir: str = "data/artifacts"
    ttl_days: int = 7
    max_bytes_per_trace: int = 52_428_800


class StmConfig(BaseModel):
    session_ttl_days: int = 30


class RoleConfig(BaseModel):
    allowed_tables: list[str] = Field(default_factory=list)
    denied_columns: list[str] = Field(default_factory=list)
    store_filter_required: bool = False


class ProjectConfig(BaseModel):
    app_name: str = "supermarket-analysis-agent"
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)
    clarification: ClarificationConfig = Field(default_factory=ClarificationConfig)
    rag: RagConfig = Field(default_factory=RagConfig)
    budget: BudgetConfig = Field(default_factory=BudgetConfig)
    policy: PolicyConfig = Field(default_factory=PolicyConfig)
    artifacts: ArtifactsConfig = Field(default_factory=ArtifactsConfig)
    stm: StmConfig = Field(default_factory=StmConfig)
    roles: dict[str, RoleConfig] = Field(default_factory=dict)


class ModelProfile(BaseModel):
    provider: str = "openrouter"
    model_id: str
    supports_vision: bool = False
    embedding_dims: int | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    reasoning: dict[str, Any] | None = None


class ModelsConfig(BaseModel):
    default_profile: str = "openrouter_mimo"
    agent_profiles: dict[str, str] = Field(default_factory=dict)
    profiles: dict[str, ModelProfile] = Field(default_factory=dict)


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@lru_cache(maxsize=1)
def load_project_config() -> ProjectConfig:
    path = ROOT / "config" / "project.yaml"
    return ProjectConfig.model_validate(_load_yaml(path))


@lru_cache(maxsize=1)
def load_models_config() -> ModelsConfig:
    path = ROOT / "config" / "models.yaml"
    return ModelsConfig.model_validate(_load_yaml(path))


def require_env(name: str, *, aliases: tuple[str, ...] = ()) -> str:
    for key in (name, *aliases):
        value = os.getenv(key)
        if value:
            return value
    raise RuntimeError(f"Missing required environment variable: {name}")


def get_openrouter_api_key() -> str:
    legacy = os.getenv("openroute_api_key")
    if legacy and not os.getenv("OPENROUTER_API_KEY"):
        import warnings

        warnings.warn("openroute_api_key is deprecated; use OPENROUTER_API_KEY", stacklevel=2)
        return legacy
    return require_env("OPENROUTER_API_KEY", aliases=("openroute_api_key",))
