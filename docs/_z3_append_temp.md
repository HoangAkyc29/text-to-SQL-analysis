
## §Z.3 — Phân tích từng dòng pipeline.py

> **Phạm vi:** Tài liệu này bổ sung §Z.2.6 bằng phân tích *sâu theo từng dòng* của `packages/project-core/src/project_core/orchestration/pipeline.py` (695 dòng logic). Không lặp lại mô tả service agent II/III/IV trong §Z.2.1–§Z.2.4; tập trung vào *orchestrator*, luồng dữ liệu, nhánh điều kiện, hợp đồng, và tương tác với gateway/policy/budget.

**Người gọi trực tiếp:** `ChatOrchestrator` (`agents/chat-gateway/src/chat_gateway/orchestrator.py` dòng 81–88 khởi tạo, `_run_pipeline_and_respond` gọi `pipeline.run`). **Test:** `packages/project-test/integration/test_pipeline_flows.py`, `test_context_policy_pipeline.py`, `test_session_budget.py`.

### §Z.3.1 — Tổng quan kiến trúc và luồng dữ liệu

`SupermarketAnalysisPipeline` là lớp điều phối **đồng bộ** (blocking) duy nhất trong monorepo thực thi chuỗi: **Agent II (SQL Planner) → PolicyEngine → Agent III (Risk) → SqlGateway execute → Agent IV (Analyst)**. Không mở HTTP, không đọc Redis; mọi I/O mạng đi qua `AgentInvoker` và `SqlGatewayClient` được inject.

```
run(brief, workflow, permissions)
  ├─ khởi tạo trace_id, acl, artifact dirs, PolicyEngine
  └─ for sql_attempt in 1..max_sql_retries:
       ├─ (tuỳ chọn) apply_data_feedback → brief
       ├─ build schema_context + invoke II
       ├─ nhánh clarify | impossible | plan_sql/probe_sql
       ├─ for mỗi SQL: policy → III loop → execute → parquet
       ├─ nếu không có query_files → continue hoặc POLICY_BLOCKED
       ├─ invoke IV với dataset + execution_plan
       └─ nhánh data_feedback | clarify | impossible | complete/partial
```

**Inbox** (`dict[str, Any]`) là bộ nhớ vòng lặp giữa các agent trong cùng một `run()`: `policy_feedback`, `risk_feedback`, `explain_plan`, `data_feedback`, `probe_mode`. Orchestrator bên ngoài không đọc inbox; chỉ agent II/III/IV nhận qua payload.

**WorkflowState** được mutate tại chỗ: `status`, `sql_attempt`, `clarify_round`, `progress_step`, `steps`, `last_outcome`. Callback `on_progress` cho phép UI/streaming cập nhật tiến độ mà không đổi semantics kết quả.

### §Z.3.2 — Dòng 1: `from __future__ import annotations`

Chỉ thị PEP 563 (hoãn đánh giá annotation) cho phép toàn file dùng cú pháp union `X | Y` (ví dụ dòng 53 `SchemaCatalog | None`) mà không cần quote string cho forward reference.

**Runtime:** Không thực thi logic nghiệp vụ — chỉ ảnh hưởng type checker.

**Edge case:** Bỏ dòng này trên Python cũ sẽ lỗi cú pháp với `| None`. Repo dùng Python 3.11+.

### §Z.3.3 — Dòng 2: dòng trống phân tách

Dòng trống sau chỉ thị `__future__` — tuân PEP 8.

### §Z.3.4 — Dòng 3–8: import stdlib và typing

| Dòng | Mã | Vai trò trong pipeline |
|------|-----|------------------------|
| 3 | `import json` | Không gọi trực tiếp; serialization qua Pydantic `model_dump(mode="json")`. |
| 4 | `import time` | `time.monotonic()` tại dòng 83, 652 — deadline sync. |
| 5 | `Callable` | Type hint `on_progress: Callable[[WorkflowState], None] | None`. |
| 6 | `Path` | Artifact dirs, parquet paths, artifact_urls. |
| 7 | `Any` | inbox, promoted_tools, inject optional stores. |
| 8 | `uuid4` | trace_id mỗi run; step_id mỗi WorkflowStep. |

**Luồng dữ liệu:** `uuid4()` → string trace gắn audit, artifact, `PipelineResult.trace_id`.

### §Z.3.5 — Dòng 9: dòng trống trước pandas

Phân tách third-party khỏi project_core.

### §Z.3.6 — Dòng 10: `import pandas as pd`

Dùng tại 397–399: `pd.DataFrame(rows)` → parquet. `rows` từ gateway `list[dict]`.

**Edge case:** `rows` rỗng → DataFrame rỗng, profile flag `empty` sau merge.

**Performance:** Toàn bộ rows vào RAM — không streaming.

### §Z.3.7 — Dòng 11: dòng trống trước project_core

Ngăn cách dependency layers.

### §Z.3.8 — Dòng 12: import `load_project_config`

```python
from project_core.config.loader import load_project_config
```

Đọc YAML/env tại __init__ 66: max_sql_retries, max_clarify_rounds, max_sync_seconds, artifacts.base_dir, iv_max_steps, max_sql_queries_per_plan, max_risk_retries.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 12.

### §Z.3.9 — Dòng 13: import `ContextPolicy`

```python
from project_core.domain.access.context_policy import ContextPolicy
```

filter_schema_excerpt 138; can_invoke_tool 302,339; can_execute_sql 350; can_invoke_function 447.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 13.

### §Z.3.10 — Dòng 14: import `decompose_brief`

```python
from project_core.domain.analysis.decomposer import decompose_brief
```

Tạo plan khi brief.plan None — một lần đầu run 112–113.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 14.

### §Z.3.11 — Dòng 15: import `build_execution_plan`

```python
from project_core.domain.analysis.execution_composer import build_execution_plan
```

Ghép subtask + parquet + candidates → execution_steps 461–467.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 15.

### §Z.3.12 — Dòng 16: import `rank_candidates`

```python
from project_core.domain.analysis.recipe_matcher import rank_candidates
```

Fallback rank khi không Mongo registry — dòng 454.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 16.

### §Z.3.13 — Dòng 17: import `AuditLogger`

```python
from project_core.domain.audit.logger import AuditLogger
```

log_sql_explain 305–312; log_sql_execute 365–396.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 17.

### §Z.3.14 — Dòng 18: import `apply_data_feedback`

```python
from project_core.domain.brief.merge import apply_data_feedback
```

Merge IV feedback vào brief — dòng 132 đầu sql_attempt.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 18.

### §Z.3.15 — Dòng 19: import `AnalystResponse, RiskReviewResponse, SqlPlannerResponse`

```python
from project_core.domain.contracts.agent_outputs import AnalystResponse, RiskReviewResponse, SqlPlannerResponse
```

Type guard sau parse II/III/IV.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 19.

### §Z.3.16 — Dòng 20: import `AnalysisBrief, TechnicalSummary`

```python
from project_core.domain.contracts.brief import AnalysisBrief, TechnicalSummary
```

Input brief; output summary mọi nhánh kết thúc.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 20.

### §Z.3.17 — Dòng 21: import `(contracts.brief tiếp)`

```python
from project_core.domain.contracts.clarification import ClarificationRequest
```

TechnicalSummary trong _finish và PipelineResult.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 21.

### §Z.3.18 — Dòng 22: import `ClarificationRequest`

```python
from project_core.domain.contracts.feedback import DataFeedback
```

Validate clarify từ II 200, IV 540, 558.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 22.

### §Z.3.19 — Dòng 23: import `DataFeedback`

```python
from project_core.domain.contracts.parse import parse_agent_response
```

Validate feedback IV 509; fallback invalid 511–517.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 23.

### §Z.3.20 — Dòng 24: import `parse_agent_response`

```python
from project_core.domain.contracts.pipeline import (
```

Raw dict → typed model; ContractInvalidError.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 24.

### §Z.3.21 — Dòng 25: import `ExtractedDataset, PipelineResult, ...`

```python
    ExtractedDataset,
```

I/O contracts pipeline.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 25.

### §Z.3.22 — Dòng 26: import `QueryResultFile`

```python
    PipelineResult,
```

Manifest parquet cho IV dataset_manifest.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 26.

### §Z.3.23 — Dòng 27: import `ResultProfile`

```python
    QueryResultFile,
```

Merged profile cho IV result_profile.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 27.

### §Z.3.24 — Dòng 28: import `(pipeline contracts)`

```python
    ResultProfile,
```

PipelineResult chứa workflow_steps, needs_clarification optional.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 28.

### §Z.3.25 — Dòng 29: import `(pipeline contracts)`

```python
)
```

ExtractedDataset trace_id + queries list.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 29.

### §Z.3.26 — Dòng 30: import `SqlAclContext`

```python
from project_core.domain.contracts.sql_acl import SqlAclContext
```

from_permissions 84; truyền gateway explain/execute.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 30.

### §Z.3.27 — Dòng 31: import `build_result_profile`

```python
from project_core.domain.sql.result_profile import build_result_profile
```

Từ DataFrame 400; merge _merge_profiles 435.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 31.

### §Z.3.28 — Dòng 32: import `AnalysisOutcome, PermissionsSnapshot, WorkflowState`

```python
from project_core.domain.contracts.workflow import (
```

Outcome enum; permissions input; workflow mutated.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 32.

### §Z.3.29 — Dòng 33: import `WorkflowStatus`

```python
    AnalysisOutcome,
```

RUNNING 89, AWAITING_CLARIFICATION 201, IDLE 667.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 33.

### §Z.3.30 — Dòng 34: import `WorkflowStep, WorkflowStepType`

```python
    PermissionsSnapshot,
```

Audit trail steps; progress_step strings.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 34.

### §Z.3.31 — Dòng 35: import `(workflow contracts)`

```python
    WorkflowState,
```

WorkflowStepType CLARIFY, POLICY_REJECT, RISK_REJECT, EXECUTE, DATA_FEEDBACK, SANDBOX.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 35.

### §Z.3.32 — Dòng 36: import `(workflow contracts)`

```python
    WorkflowStatus,
```

WorkflowStep ghi sql_attempt, query_index, summary.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 36.

### §Z.3.33 — Dòng 37: import `(workflow contracts)`

```python
    WorkflowStep,
```

AnalysisOutcome SUCCESS, PARTIAL, ERROR, IMPOSSIBLE, POLICY_BLOCKED, NEEDS_CLARIFICATION.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 37.

### §Z.3.34 — Dòng 38: import `(workflow contracts)`

```python
    WorkflowStepType,
```

PermissionsSnapshot model_dump json cho agent payload.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 38.

### §Z.3.35 — Dòng 39: import `(workflow contracts)`

```python
)
```

WorkflowState active_analysis_id cho resume.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 39.

### §Z.3.36 — Dòng 40: import `ClarifyRoundsExceededError, ContractInvalidError`

```python
from project_core.domain.errors.codes import ClarifyRoundsExceededError, ContractInvalidError
```

Raise 198; catch parse 166,280,489.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 40.

### §Z.3.37 — Dòng 41: import `AgentInvoker, SqlGatewayClient, SupermarketBudgetGuard, TraceBudget`

```python
from project_core.domain.budget import AgentInvoker, SqlGatewayClient, SupermarketBudgetGuard, TraceBudget
```

Inject; budget.record II/III/IV.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 41.

### §Z.3.38 — Dòng 42: import `PolicyEngine`

```python
from project_core.domain.sql.policy_engine import PolicyEngine
```

validate SQL 239.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 42.

### §Z.3.39 — Dòng 43: import `suggest_query_plan`

```python
from project_core.domain.sql.shard_resolver import suggest_query_plan
```

Shard routing 136.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 43.

### §Z.3.40 — Dòng 44: import `SchemaCatalog`

```python
from project_core.domain.schema.catalog import SchemaCatalog
```

Inject hoặc from_dictionary_dir 61.

**Liên hệ caller:** ChatOrchestrator và test conftest inject cùng bộ dependency tương ứng dòng 44.

### §Z.3.41 — Dòng 45–46: dòng trống trước class

Hai dòng trống phân tách imports và định nghĩa class.

### §Z.3.42 — Dòng 47: `__init__` / class

```python
class SupermarketAnalysisPipeline:
```

Định nghĩa `class SupermarketAnalysisPipeline` — orchestrator đồng bộ, không kế thừa.

### §Z.3.43 — Dòng 48: `__init__` / class

```python
    def __init__(
```

Bắt đầu `def __init__(`.

### §Z.3.44 — Dòng 49: `__init__` / class

```python
        self,
```

Tham số `self`.

### §Z.3.45 — Dòng 50: `__init__` / class

```python
        *,
```

`*` — mọi tham số sau là keyword-only.

### §Z.3.46 — Dòng 51: `__init__` / class

```python
        agent_invoker: AgentInvoker,
```

`agent_invoker: AgentInvoker` — bắt buộc; HttpAgentInvoker production.

### §Z.3.47 — Dòng 52: `__init__` / class

```python
        sql_gateway: SqlGatewayClient,
```

`sql_gateway: SqlGatewayClient` — bắt buộc; explain + execute_readonly.

### §Z.3.48 — Dòng 53: `__init__` / class

```python
        catalog: SchemaCatalog | None = None,
```

`catalog: SchemaCatalog | None = None` — default from_dictionary_dir 61.

### §Z.3.49 — Dòng 54: `__init__` / class

```python
        feedback_loop: Any | None = None,
```

`feedback_loop: Any | None` — RAG retrieve + on_pipeline_complete.

### §Z.3.50 — Dòng 55: `__init__` / class

```python
        analysis_tool_registry: Any | None = None,
```

`analysis_tool_registry: Any | None` — Mongo tools promote/stage.

### §Z.3.51 — Dòng 56: `__init__` / class

```python
        domain_rule_store: Any | None = None,
```

`domain_rule_store: Any | None` — domain rules excerpt + stage.

### §Z.3.52 — Dòng 57: `__init__` / class

```python
        audit_logger: AuditLogger | None = None,
```

`audit_logger: AuditLogger | None` — default AuditLogger 65.

### §Z.3.53 — Dòng 58: `__init__` / class

```python
    ) -> None:
```

`) -> None:` — constructor.

### §Z.3.54 — Dòng 59: `__init__` / class

```python
        self.agent_invoker = agent_invoker
```

Gán `self.agent_invoker`.

### §Z.3.55 — Dòng 60: `__init__` / class

```python
        self.sql_gateway = sql_gateway
```

Gán `self.sql_gateway`.

### §Z.3.56 — Dòng 61: `__init__` / class

```python
        self.catalog = catalog or SchemaCatalog.from_dictionary_dir()
```

`self.catalog = catalog or SchemaCatalog.from_dictionary_dir()`.

### §Z.3.57 — Dòng 62: `__init__` / class

```python
        self.feedback_loop = feedback_loop
```

Gán `self.feedback_loop` — có thể None.

### §Z.3.58 — Dòng 63: `__init__` / class

```python
        self.analysis_tool_registry = analysis_tool_registry
```

Gán `self.analysis_tool_registry` — có thể None.

### §Z.3.59 — Dòng 64: `__init__` / class

```python
        self.domain_rule_store = domain_rule_store
```

Gán `self.domain_rule_store` — có thể None.

### §Z.3.60 — Dòng 65: `__init__` / class

```python
        self.audit = audit_logger or AuditLogger()
```

`self.audit = audit_logger or AuditLogger()`.

### §Z.3.61 — Dòng 66: `__init__` / class

```python
        self.cfg = load_project_config()
```

`self.cfg = load_project_config()` — một lần mỗi pipeline instance.

### §Z.3.62 — Dòng 67: `__init__` / class

```python
        self.context_policy = ContextPolicy()
```

`self.context_policy = ContextPolicy()` — stateless policy checks.

### §Z.3.63 — Dòng 69: chữ ký `run()`

```python
    def run(
```

Bắt đầu `def run(` — entry point phân tích.

### §Z.3.64 — Dòng 70: chữ ký `run()`

```python
        self,
```

`self,`.

### §Z.3.65 — Dòng 71: chữ ký `run()`

```python
        *,
```

Keyword-only `*,`.

### §Z.3.66 — Dòng 72: chữ ký `run()`

```python
        brief: AnalysisBrief,
```

`brief: AnalysisBrief` — intent, plan, exploration_mode, user_knowledge_level.

### §Z.3.67 — Dòng 73: chữ ký `run()`

```python
        workflow: WorkflowState,
```

`workflow: WorkflowState` — mutate status, steps, clarify_round.

### §Z.3.68 — Dòng 74: chữ ký `run()`

```python
        permissions: PermissionsSnapshot,
```

`permissions: PermissionsSnapshot` — ACL tables, columns, store, tool grants.

### §Z.3.69 — Dòng 75: chữ ký `run()`

```python
        trace_budget: TraceBudget | None = None,
```

`trace_budget: TraceBudget | None` — session budget từ orchestrator.

### §Z.3.70 — Dòng 76: chữ ký `run()`

```python
        on_progress: Callable[[WorkflowState], None] | None = None,
```

`on_progress` callback optional — UI progress_step.

### §Z.3.71 — Dòng 77: chữ ký `run()`

```python
        deadline: float | None = None,
```

`deadline: float | None` — monotonic absolute; orchestrator có thể set.

### §Z.3.72 — Dòng 78: chữ ký `run()`

```python
    ) -> PipelineResult:
```

`) -> PipelineResult:` — outcome, technical_summary, workflow_steps, needs_clarification optional.

### §Z.3.73 — Dòng 79: `trace_id = str(uuid4())`

```python
        trace_id = str(uuid4())
```

**Nhãn:** trace_id

**Mô tả:** Sinh UUID4 string — định danh duy nhất mỗi run; không tái sử dụng.

**Vị trí file:** `pipeline.py` dòng 79 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 79; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.74 — Dòng 80: `analysis_id = workflow.active_analysis_id or trace_id`

```python
        analysis_id = workflow.active_analysis_id or trace_id
```

**Nhãn:** analysis_id

**Mô tả:** Ưu tiên workflow.active_analysis_id (resume) else trace_id.

**Vị trí file:** `pipeline.py` dòng 80 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 80; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.75 — Dòng 81: `sync_deadline = deadline`

```python
        sync_deadline = deadline
```

**Nhãn:** sync_deadline

**Mô tả:** Lưu deadline caller — có thể None.

**Vị trí file:** `pipeline.py` dòng 81 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 81; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.76 — Dòng 82: `if sync_deadline is None and self.cfg.pipeline.max_sync_seco...`

```python
        if sync_deadline is None and self.cfg.pipeline.max_sync_seconds:
```

**Nhãn:** max_sync_seconds

**Mô tả:** Nếu deadline None và config truthy, tự tính deadline nội bộ.

**Vị trí file:** `pipeline.py` dòng 82 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 82; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.77 — Dòng 83: `sync_deadline = time.monotonic() + float(self.cfg.pipeline.m...`

```python
            sync_deadline = time.monotonic() + float(self.cfg.pipeline.max_sync_seconds)
```

**Nhãn:** monotonic deadline

**Mô tả:** sync_deadline = monotonic() + float(max_sync_seconds).

**Vị trí file:** `pipeline.py` dòng 83 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 83; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.78 — Dòng 84: `acl = SqlAclContext.from_permissions(permissions)`

```python
        acl = SqlAclContext.from_permissions(permissions)
```

**Nhãn:** acl

**Mô tả:** SqlAclContext.from_permissions — actor, role cho gateway.

**Vị trí file:** `pipeline.py` dòng 84 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 84; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.79 — Dòng 85: `if hasattr(self.agent_invoker, "set_trace"):`

```python
        if hasattr(self.agent_invoker, "set_trace"):
```

**Nhãn:** set_trace invoker

**Mô tả:** Duck typing hasattr agent_invoker set_trace.

**Invoke agent:** Payload dict; metadata mode plan_sql/review/analyze. Lỗi HTTP propagate — pipeline không catch network.

**Vị trí file:** `pipeline.py` dòng 85 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 85; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.80 — Dòng 86: `self.agent_invoker.set_trace(trace_id=trace_id, analysis_id=...`

```python
            self.agent_invoker.set_trace(trace_id=trace_id, analysis_id=analysis_id)  # type: ignore[attr-defined]
```

**Nhãn:** invoke set_trace

**Mô tả:** Gắn trace_id, analysis_id cho HTTP logging downstream.

**Invoke agent:** Payload dict; metadata mode plan_sql/review/analyze. Lỗi HTTP propagate — pipeline không catch network.

**Vị trí file:** `pipeline.py` dòng 86 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 86; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.81 — Dòng 87: `if hasattr(self.sql_gateway, "set_trace"):`

```python
        if hasattr(self.sql_gateway, "set_trace"):
```

**Nhãn:** set_trace gateway

**Mô tả:** Gateway set_trace(trace_id).

**Vị trí file:** `pipeline.py` dòng 87 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 87; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.82 — Dòng 88: `self.sql_gateway.set_trace(trace_id)  # type: ignore[attr-de...`

```python
            self.sql_gateway.set_trace(trace_id)  # type: ignore[attr-defined]
```

**Nhãn:** end set_trace

**Mô tả:** Kết thúc block trace propagation.

**Vị trí file:** `pipeline.py` dòng 88 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 88; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.83 — Dòng 89: `workflow.status = WorkflowStatus.RUNNING`

```python
        workflow.status = WorkflowStatus.RUNNING
```

**Nhãn:** RUNNING

**Mô tả:** workflow.status = RUNNING — signal đang xử lý.

**Vị trí file:** `pipeline.py` dòng 89 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 89; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.84 — Dòng 90: `workflow.sql_attempt = 1`

```python
        workflow.sql_attempt = 1
```

**Nhãn:** sql_attempt=1

**Mô tả:** Reset trước vòng lặp; cập nhật mỗi iteration 130.

**Vị trí file:** `pipeline.py` dòng 90 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 90; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.85 — Dòng 91: `budget = SupermarketBudgetGuard(trace_budget or TraceBudget(...`

```python
        budget = SupermarketBudgetGuard(trace_budget or TraceBudget())
```

**Nhãn:** budget guard

**Mô tả:** SupermarketBudgetGuard(trace_budget or TraceBudget()).

**Vị trí file:** `pipeline.py` dòng 91 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 91; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.86 — Dòng 92: `artifact_base = Path(self.cfg.artifacts.base_dir) / trace_id`

```python
        artifact_base = Path(self.cfg.artifacts.base_dir) / trace_id
```

**Nhãn:** artifact_base

**Mô tả:** Path(cfg.artifacts.base_dir) / trace_id.

**Vị trí file:** `pipeline.py` dòng 92 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 92; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.87 — Dòng 93: `raw_dir = artifact_base / "raw"`

```python
        raw_dir = artifact_base / "raw"
```

**Nhãn:** raw_dir

**Mô tả:** artifact_base / raw — parquet queries.

**Vị trí file:** `pipeline.py` dòng 93 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 93; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.88 — Dòng 94: `out_dir = artifact_base / "out"`

```python
        out_dir = artifact_base / "out"
```

**Nhãn:** out_dir

**Mô tả:** artifact_base / out — IV artifacts.

**Vị trí file:** `pipeline.py` dòng 94 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 94; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.89 — Dòng 95: `raw_dir.mkdir(parents=True, exist_ok=True)`

```python
        raw_dir.mkdir(parents=True, exist_ok=True)
```

**Nhãn:** mkdir raw

**Mô tả:** parents=True, exist_ok=True.

**Vị trí file:** `pipeline.py` dòng 95 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 95; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.90 — Dòng 96: `out_dir.mkdir(parents=True, exist_ok=True)`

```python
        out_dir.mkdir(parents=True, exist_ok=True)
```

**Nhãn:** mkdir out

**Mô tả:** Tương tự raw_dir.

**Vị trí file:** `pipeline.py` dòng 96 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 96; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.91 — Dòng 97: ``

```python

```

**Nhãn:** L97

**Mô tả:** Hành vi dòng 97.

**Vị trí file:** `pipeline.py` dòng 97 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 97; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.92 — Dòng 98: `policy = PolicyEngine(`

```python
        policy = PolicyEngine(
```

**Nhãn:** PolicyEngine

**Mô tả:** Khởi tạo với catalog + 4 chiều permission.

**Vị trí file:** `pipeline.py` dòng 98 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 98; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.93 — Dòng 99: `self.catalog,`

```python
            self.catalog,
```

**Nhãn:** catalog arg

**Mô tả:** self.catalog schema dictionary.

**Vị trí file:** `pipeline.py` dòng 99 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 99; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.94 — Dòng 100: `allowed_tables=permissions.allowed_tables,`

```python
            allowed_tables=permissions.allowed_tables,
```

**Nhãn:** allowed_tables

**Mô tả:** Whitelist bảng từ permissions.

**Vị trí file:** `pipeline.py` dòng 100 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 100; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.95 — Dòng 101: `denied_columns=permissions.denied_columns,`

```python
            denied_columns=permissions.denied_columns,
```

**Nhãn:** denied_columns

**Mô tả:** Cột cấm SELECT.

**Vị trí file:** `pipeline.py` dòng 101 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 101; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.96 — Dòng 102: `store_ids=permissions.store_ids,`

```python
            store_ids=permissions.store_ids,
```

**Nhãn:** store_ids

**Mô tả:** Filter cửa hàng.

**Vị trí file:** `pipeline.py` dòng 102 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 102; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.97 — Dòng 103: `store_filter_required=permissions.store_filter_required,`

```python
            store_filter_required=permissions.store_filter_required,
```

**Nhãn:** store_filter_required

**Mô tả:** Engine inject WHERE store.

**Vị trí file:** `pipeline.py` dòng 103 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 103; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.98 — Dòng 104: `)`

```python
        )
```

**Nhãn:** end PolicyEngine

**Mô tả:** Đóng constructor.

**Vị trí file:** `pipeline.py` dòng 104 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 104; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.99 — Dòng 105: ``

```python

```

**Nhãn:** L105

**Mô tả:** Hành vi dòng 105.

**Vị trí file:** `pipeline.py` dòng 105 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 105; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.100 — Dòng 106: `inbox: dict[str, Any] = {}`

```python
        inbox: dict[str, Any] = {}
```

**Nhãn:** inbox

**Mô tả:** dict mutable xuyên sql_attempt và query loop.

**Vị trí file:** `pipeline.py` dòng 106 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 106; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.101 — Dòng 107: `needs_clarification: ClarificationRequest | None = None`

```python
        needs_clarification: ClarificationRequest | None = None
```

**Nhãn:** needs_clarification

**Mô tả:** Khởi tạo None; set khi return clarify.

**Vị trí file:** `pipeline.py` dòng 107 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 107; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.102 — Dòng 108: `domain_excerpt = ""`

```python
        domain_excerpt = ""
```

**Nhãn:** domain_excerpt

**Mô tả:** Chuỗi rỗng mặc định.

**Vị trí file:** `pipeline.py` dòng 108 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 108; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.103 — Dòng 109: `if self.domain_rule_store is not None:`

```python
        if self.domain_rule_store is not None:
```

**Nhãn:** domain_rule_store check

**Mô tả:** if not None lấy excerpt.

**Vị trí file:** `pipeline.py` dòng 109 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 109; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.104 — Dòng 110: `domain_excerpt = self.domain_rule_store.excerpt_for_agents()`

```python
            domain_excerpt = self.domain_rule_store.excerpt_for_agents()
```

**Nhãn:** excerpt_for_agents

**Mô tả:** Text rút gọn domain rules.

**Vị trí file:** `pipeline.py` dòng 110 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 110; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.105 — Dòng 111: ``

```python

```

**Nhãn:** L111

**Mô tả:** Hành vi dòng 111.

**Vị trí file:** `pipeline.py` dòng 111 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 111; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.106 — Dòng 112: `if brief.plan is None:`

```python
        if brief.plan is None:
```

**Nhãn:** plan None check

**Mô tả:** if brief.plan is None decompose.

**Vị trí file:** `pipeline.py` dòng 112 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 112; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.107 — Dòng 113: `brief.plan = decompose_brief(brief)`

```python
            brief.plan = decompose_brief(brief)
```

**Nhãn:** decompose_brief

**Mô tả:** Mutate brief.plan tại chỗ.

**Vị trí file:** `pipeline.py` dòng 113 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 113; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.108 — Dòng 114: ``

```python

```

**Nhãn:** L114

**Mô tả:** Hành vi dòng 114.

**Vị trí file:** `pipeline.py` dòng 114 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 114; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.109 — Dòng 115: `promoted_tools: list[dict[str, Any]] = []`

```python
        promoted_tools: list[dict[str, Any]] = []
```

**Nhãn:** promoted_tools

**Mô tả:** List rỗng mặc định.

**Vị trí file:** `pipeline.py` dòng 115 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 115; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.110 — Dòng 116: `if self.analysis_tool_registry is not None:`

```python
        if self.analysis_tool_registry is not None:
```

**Nhãn:** registry check

**Mô tả:** if analysis_tool_registry find_promoted.

**Vị trí file:** `pipeline.py` dòng 116 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 116; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.111 — Dòng 117: `promoted_tools = self.analysis_tool_registry.find_promoted()`

```python
            promoted_tools = self.analysis_tool_registry.find_promoted()
```

**Nhãn:** find_promoted

**Mô tả:** Recipe đã promote cho IV.

**Vị trí file:** `pipeline.py` dòng 117 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 117; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.112 — Dòng 118: ``

```python

```

**Nhãn:** L118

**Mô tả:** Hành vi dòng 118.

**Vị trí file:** `pipeline.py` dòng 118 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 118; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.113 — Dòng 119: `for sql_attempt in range(1, self.cfg.pipeline.max_sql_retrie...`

```python
        for sql_attempt in range(1, self.cfg.pipeline.max_sql_retries + 1):
```

**Nhãn:** for sql_attempt

**Mô tả:** range(1, max_sql_retries + 1).

**Vị trí file:** `pipeline.py` dòng 119 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 119; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.114 — Dòng 120: `if self._deadline_exceeded(sync_deadline):`

```python
            if self._deadline_exceeded(sync_deadline):
```

**Nhãn:** deadline check

**Mô tả:** _deadline_exceeded sync_deadline.

**Vị trí file:** `pipeline.py` dòng 120 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 120; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.115 — Dòng 121: `return self._finish(`

```python
                return self._finish(
```

**Nhãn:** deadline exceeded

**Mô tả:** return _finish ERROR sync_deadline_exceeded.

**_finish:** workflow IDLE, last_outcome, PipelineResult không needs_clarification.

**Vị trí file:** `pipeline.py` dòng 121 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 121; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.116 — Dòng 122: `trace_id,`

```python
                    trace_id,
```

**Nhãn:** L122

**Mô tả:** Hành vi dòng 122.

**Vị trí file:** `pipeline.py` dòng 122 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 122; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.117 — Dòng 123: `workflow,`

```python
                    workflow,
```

**Nhãn:** L123

**Mô tả:** Hành vi dòng 123.

**Vị trí file:** `pipeline.py` dòng 123 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 123; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.118 — Dòng 124: `AnalysisOutcome.ERROR,`

```python
                    AnalysisOutcome.ERROR,
```

**Nhãn:** L124

**Mô tả:** Hành vi dòng 124.

**Vị trí file:** `pipeline.py` dòng 124 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 124; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.119 — Dòng 125: `TechnicalSummary(`

```python
                    TechnicalSummary(
```

**Nhãn:** L125

**Mô tả:** Hành vi dòng 125.

**Vị trí file:** `pipeline.py` dòng 125 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 125; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.120 — Dòng 126: `outcome=AnalysisOutcome.ERROR.value,`

```python
                        outcome=AnalysisOutcome.ERROR.value,
```

**Nhãn:** L126

**Mô tả:** Hành vi dòng 126.

**Vị trí file:** `pipeline.py` dòng 126 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 126; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.121 — Dòng 127: `caveats=["sync_deadline_exceeded"],`

```python
                        caveats=["sync_deadline_exceeded"],
```

**Nhãn:** L127

**Mô tả:** Hành vi dòng 127.

**Vị trí file:** `pipeline.py` dòng 127 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 127; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.122 — Dòng 128: `),`

```python
                    ),
```

**Nhãn:** L128

**Mô tả:** Hành vi dòng 128.

**Vị trí file:** `pipeline.py` dòng 128 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 128; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.123 — Dòng 129: `)`

```python
                )
```

**Nhãn:** L129

**Mô tả:** Hành vi dòng 129.

**Vị trí file:** `pipeline.py` dòng 129 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 129; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.124 — Dòng 130: `workflow.sql_attempt = sql_attempt`

```python
            workflow.sql_attempt = sql_attempt
```

**Nhãn:** sql_attempt assign

**Mô tả:** workflow.sql_attempt = sql_attempt.

**Vị trí file:** `pipeline.py` dòng 130 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 130; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.125 — Dòng 131: `if inbox.get("data_feedback"):`

```python
            if inbox.get("data_feedback"):
```

**Nhãn:** data_feedback check

**Mô tả:** if inbox.get data_feedback.

**Vị trí file:** `pipeline.py` dòng 131 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 131; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.126 — Dòng 132: `brief = apply_data_feedback(brief, inbox["data_feedback"])`

```python
                brief = apply_data_feedback(brief, inbox["data_feedback"])
```

**Nhãn:** apply_data_feedback

**Mô tả:** Merge feedback IV vào brief.

**Inbox:** Agent sau trong cùng run đọc qua payload — II nhận full inbox 156.

**Vị trí file:** `pipeline.py` dòng 132 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 132; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.127 — Dòng 133: ``

```python

```

**Nhãn:** L133

**Mô tả:** Hành vi dòng 133.

**Vị trí file:** `pipeline.py` dòng 133 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 133; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.128 — Dòng 134: `budget.record("II")`

```python
            budget.record("II")
```

**Nhãn:** budget II

**Mô tả:** budget.record II mỗi sql_attempt.

**Vị trí file:** `pipeline.py` dòng 134 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 134; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.129 — Dòng 135: `schema_context = self.catalog.agent_schema_bundle(permission...`

```python
            schema_context = self.catalog.agent_schema_bundle(permissions.allowed_tables)
```

**Nhãn:** schema bundle

**Mô tả:** agent_schema_bundle allowed_tables.

**Vị trí file:** `pipeline.py` dòng 135 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 135; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.130 — Dòng 136: `shard_plan = suggest_query_plan(brief.model_dump(), self.cat...`

```python
            shard_plan = suggest_query_plan(brief.model_dump(), self.catalog)
```

**Nhãn:** shard plan

**Mô tả:** suggest_query_plan brief + catalog.

**model_dump:** JSON-serializable cho HTTP agent; permissions dùng mode="json".

**Vị trí file:** `pipeline.py` dòng 136 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 136; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.131 — Dòng 137: `schema_context = {**schema_context, "shard_plan": shard_plan...`

```python
            schema_context = {**schema_context, "shard_plan": shard_plan.model_dump()}
```

**Nhãn:** merge shard

**Mô tả:** schema_context shard_plan key.

**model_dump:** JSON-serializable cho HTTP agent; permissions dùng mode="json".

**Vị trí file:** `pipeline.py` dòng 137 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 137; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.132 — Dòng 138: `filtered_snapshot = self.context_policy.filter_schema_excerp...`

```python
            filtered_snapshot = self.context_policy.filter_schema_excerpt(
```

**Nhãn:** filter snapshot

**Mô tả:** context_policy.filter_schema_excerpt.

**ContextPolicy:** Gate quyền tool/function/SQL — POLICY_BLOCKED nếu thiếu grant.

**Vị trí file:** `pipeline.py` dòng 138 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 138; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.133 — Dòng 139: `permissions, self.catalog.snapshot()`

```python
                permissions, self.catalog.snapshot()
```

**Nhãn:** L139

**Mô tả:** Hành vi dòng 139.

**Vị trí file:** `pipeline.py` dòng 139 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 139; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.134 — Dòng 140: `)`

```python
            )
```

**Nhãn:** L140

**Mô tả:** Hành vi dòng 140.

**Vị trí file:** `pipeline.py` dòng 140 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 140; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.135 — Dòng 141: `if filtered_snapshot:`

```python
            if filtered_snapshot:
```

**Nhãn:** L141

**Mô tả:** Hành vi dòng 141.

**Vị trí file:** `pipeline.py` dòng 141 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 141; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.136 — Dòng 142: `schema_context = {**schema_context, "filtered_table_snapshot...`

```python
                schema_context = {**schema_context, "filtered_table_snapshot": filtered_snapshot}
```

**Nhãn:** L142

**Mô tả:** Hành vi dòng 142.

**Vị trí file:** `pipeline.py` dòng 142 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 142; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.137 — Dòng 143: `if domain_excerpt:`

```python
            if domain_excerpt:
```

**Nhãn:** L143

**Mô tả:** Hành vi dòng 143.

**Vị trí file:** `pipeline.py` dòng 143 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 143; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.138 — Dòng 144: `schema_context = {**schema_context, "domain_rules_excerpt": ...`

```python
                schema_context = {**schema_context, "domain_rules_excerpt": domain_excerpt}
```

**Nhãn:** L144

**Mô tả:** Hành vi dòng 144.

**Vị trí file:** `pipeline.py` dòng 144 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 144; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.139 — Dòng 145: `retrieval_context: list[Any] = []`

```python
            retrieval_context: list[Any] = []
```

**Nhãn:** L145

**Mô tả:** Hành vi dòng 145.

**Vị trí file:** `pipeline.py` dòng 145 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 145; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.140 — Dòng 146: `if self.feedback_loop is not None:`

```python
            if self.feedback_loop is not None:
```

**Nhãn:** L146

**Mô tả:** Hành vi dòng 146.

**Vị trí file:** `pipeline.py` dòng 146 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 146; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.141 — Dòng 147: `retrieval_context = self.feedback_loop.retrieve_context("II"...`

```python
                retrieval_context = self.feedback_loop.retrieve_context("II", brief.intent, permissions.actor_id)
```

**Nhãn:** L147

**Mô tả:** Hành vi dòng 147.

**Vị trí file:** `pipeline.py` dòng 147 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 147; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.142 — Dòng 148: ``

```python

```

**Nhãn:** L148

**Mô tả:** Hành vi dòng 148.

**Vị trí file:** `pipeline.py` dòng 148 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 148; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.143 — Dòng 149: `workflow.progress_step = WorkflowStepType.PLAN_SQL.value`

```python
            workflow.progress_step = WorkflowStepType.PLAN_SQL.value
```

**Nhãn:** PLAN_SQL progress

**Mô tả:** workflow.progress_step PLAN_SQL.

**Vị trí file:** `pipeline.py` dòng 149 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 149; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.144 — Dòng 150: `self._emit_progress(workflow, on_progress)`

```python
            self._emit_progress(workflow, on_progress)
```

**Nhãn:** emit progress II

**Mô tả:** _emit_progress before invoke II.

**Vị trí file:** `pipeline.py` dòng 150 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 150; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.145 — Dòng 151: ``

```python

```

**Nhãn:** L151

**Mô tả:** Hành vi dòng 151.

**Vị trí file:** `pipeline.py` dòng 151 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 151; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.146 — Dòng 152: `ii_result = self.agent_invoker.invoke(`

```python
            ii_result = self.agent_invoker.invoke(
```

**Nhãn:** invoke II

**Mô tả:** agent_invoker II plan_sql mode.

**Invoke agent:** Payload dict; metadata mode plan_sql/review/analyze. Lỗi HTTP propagate — pipeline không catch network.

**Vị trí file:** `pipeline.py` dòng 152 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 152; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.147 — Dòng 153: `"II",`

```python
                "II",
```

**Nhãn:** L153

**Mô tả:** Hành vi dòng 153.

**Vị trí file:** `pipeline.py` dòng 153 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 153; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.148 — Dòng 154: `{`

```python
                {
```

**Nhãn:** L154

**Mô tả:** Hành vi dòng 154.

**Vị trí file:** `pipeline.py` dòng 154 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 154; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.149 — Dòng 155: `"brief": brief.model_dump(),`

```python
                    "brief": brief.model_dump(),
```

**Nhãn:** L155

**Mô tả:** Hành vi dòng 155.

**model_dump:** JSON-serializable cho HTTP agent; permissions dùng mode="json".

**Vị trí file:** `pipeline.py` dòng 155 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 155; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.150 — Dòng 156: `"inbox": inbox,`

```python
                    "inbox": inbox,
```

**Nhãn:** L156

**Mô tả:** Hành vi dòng 156.

**Vị trí file:** `pipeline.py` dòng 156 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 156; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.151 — Dòng 157: `"attempt": sql_attempt,`

```python
                    "attempt": sql_attempt,
```

**Nhãn:** L157

**Mô tả:** Hành vi dòng 157.

**Vị trí file:** `pipeline.py` dòng 157 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 157; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.152 — Dòng 158: `"schema_context": schema_context,`

```python
                    "schema_context": schema_context,
```

**Nhãn:** L158

**Mô tả:** Hành vi dòng 158.

**Vị trí file:** `pipeline.py` dòng 158 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 158; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.153 — Dòng 159: `"retrieval_context": [getattr(c, "text", str(c)) for c in re...`

```python
                    "retrieval_context": [getattr(c, "text", str(c)) for c in retrieval_context],
```

**Nhãn:** L159

**Mô tả:** Hành vi dòng 159.

**Vị trí file:** `pipeline.py` dòng 159 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 159; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.154 — Dòng 160: `"permissions": permissions.model_dump(mode="json"),`

```python
                    "permissions": permissions.model_dump(mode="json"),
```

**Nhãn:** L160

**Mô tả:** Hành vi dòng 160.

**model_dump:** JSON-serializable cho HTTP agent; permissions dùng mode="json".

**Vị trí file:** `pipeline.py` dòng 160 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 160; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.155 — Dòng 161: `},`

```python
                },
```

**Nhãn:** L161

**Mô tả:** Hành vi dòng 161.

**Vị trí file:** `pipeline.py` dòng 161 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 161; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.156 — Dòng 162: `{"mode": "plan_sql"},`

```python
                {"mode": "plan_sql"},
```

**Nhãn:** L162

**Mô tả:** Hành vi dòng 162.

**Vị trí file:** `pipeline.py` dòng 162 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 162; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.157 — Dòng 163: `)`

```python
            )
```

**Nhãn:** L163

**Mô tả:** Hành vi dòng 163.

**Vị trí file:** `pipeline.py` dòng 163 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 163; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.158 — Dòng 164: `try:`

```python
            try:
```

**Nhãn:** L164

**Mô tả:** Hành vi dòng 164.

**Vị trí file:** `pipeline.py` dòng 164 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 164; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.159 — Dòng 165: `ii_parsed = parse_agent_response("II", ii_result)`

```python
                ii_parsed = parse_agent_response("II", ii_result)
```

**Nhãn:** L165

**Mô tả:** Hành vi dòng 165.

**Vị trí file:** `pipeline.py` dòng 165 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 165; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.160 — Dòng 166: `except ContractInvalidError as exc:`

```python
            except ContractInvalidError as exc:
```

**Nhãn:** L166

**Mô tả:** Hành vi dòng 166.

**Vị trí file:** `pipeline.py` dòng 166 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 166; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.161 — Dòng 167: `return self._finish(`

```python
                return self._finish(
```

**Nhãn:** L167

**Mô tả:** Hành vi dòng 167.

**_finish:** workflow IDLE, last_outcome, PipelineResult không needs_clarification.

**Vị trí file:** `pipeline.py` dòng 167 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 167; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.162 — Dòng 168: `trace_id,`

```python
                    trace_id,
```

**Nhãn:** L168

**Mô tả:** Hành vi dòng 168.

**Vị trí file:** `pipeline.py` dòng 168 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 168; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.163 — Dòng 169: `workflow,`

```python
                    workflow,
```

**Nhãn:** L169

**Mô tả:** Hành vi dòng 169.

**Vị trí file:** `pipeline.py` dòng 169 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 169; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.164 — Dòng 170: `AnalysisOutcome.ERROR,`

```python
                    AnalysisOutcome.ERROR,
```

**Nhãn:** L170

**Mô tả:** Hành vi dòng 170.

**Vị trí file:** `pipeline.py` dòng 170 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 170; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.165 — Dòng 171: `TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveat...`

```python
                    TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveats=[str(exc)]),
```

**Nhãn:** L171

**Mô tả:** Hành vi dòng 171.

**Vị trí file:** `pipeline.py` dòng 171 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 171; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.166 — Dòng 172: `)`

```python
                )
```

**Nhãn:** L172

**Mô tả:** Hành vi dòng 172.

**Vị trí file:** `pipeline.py` dòng 172 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 172; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.167 — Dòng 173: `if not isinstance(ii_parsed, SqlPlannerResponse):`

```python
            if not isinstance(ii_parsed, SqlPlannerResponse):
```

**Nhãn:** L173

**Mô tả:** Hành vi dòng 173.

**Vị trí file:** `pipeline.py` dòng 173 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 173; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.168 — Dòng 174: `return self._finish(`

```python
                return self._finish(
```

**Nhãn:** L174

**Mô tả:** Hành vi dòng 174.

**_finish:** workflow IDLE, last_outcome, PipelineResult không needs_clarification.

**Vị trí file:** `pipeline.py` dòng 174 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 174; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.169 — Dòng 175: `trace_id,`

```python
                    trace_id,
```

**Nhãn:** L175

**Mô tả:** Hành vi dòng 175.

**Vị trí file:** `pipeline.py` dòng 175 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 175; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.170 — Dòng 176: `workflow,`

```python
                    workflow,
```

**Nhãn:** L176

**Mô tả:** Hành vi dòng 176.

**Vị trí file:** `pipeline.py` dòng 176 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 176; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.171 — Dòng 177: `AnalysisOutcome.ERROR,`

```python
                    AnalysisOutcome.ERROR,
```

**Nhãn:** L177

**Mô tả:** Hành vi dòng 177.

**Vị trí file:** `pipeline.py` dòng 177 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 177; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.172 — Dòng 178: `TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveat...`

```python
                    TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveats=["invalid_agent_ii"]),
```

**Nhãn:** L178

**Mô tả:** Hành vi dòng 178.

**Vị trí file:** `pipeline.py` dòng 178 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 178; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.173 — Dòng 179: `)`

```python
                )
```

**Nhãn:** L179

**Mô tả:** Hành vi dòng 179.

**Vị trí file:** `pipeline.py` dòng 179 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 179; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.174 — Dòng 180: `action = ii_parsed.action`

```python
            action = ii_parsed.action
```

**Nhãn:** action II

**Mô tả:** action = ii_parsed.action — phân nhánh chính.

**Vị trí file:** `pipeline.py` dòng 180 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 180; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.175 — Dòng 181: ``

```python

```

**Nhãn:** L181

**Mô tả:** Hành vi dòng 181.

**Vị trí file:** `pipeline.py` dòng 181 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 181; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.176 — Dòng 182: `if action == "clarify" and not brief.exploration_mode:`

```python
            if action == "clarify" and not brief.exploration_mode:
```

**Nhãn:** clarify check

**Mô tả:** action clarify and not exploration_mode.

**Vị trí file:** `pipeline.py` dòng 182 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 182; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.177 — Dòng 183: `workflow.clarify_round += 1`

```python
                workflow.clarify_round += 1
```

**Nhãn:** L183

**Mô tả:** Hành vi dòng 183.

**Vị trí file:** `pipeline.py` dòng 183 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 183; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.178 — Dòng 184: `workflow.steps.append(`

```python
                workflow.steps.append(
```

**Nhãn:** L184

**Mô tả:** Hành vi dòng 184.

**Vị trí file:** `pipeline.py` dòng 184 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 184; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.179 — Dòng 185: `WorkflowStep(`

```python
                    WorkflowStep(
```

**Nhãn:** L185

**Mô tả:** Hành vi dòng 185.

**WorkflowStep:** step_id UUID mới; orchestrator persist workflow qua Redis sau run.

**Vị trí file:** `pipeline.py` dòng 185 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 185; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.180 — Dòng 186: `step_id=str(uuid4()),`

```python
                        step_id=str(uuid4()),
```

**Nhãn:** L186

**Mô tả:** Hành vi dòng 186.

**Vị trí file:** `pipeline.py` dòng 186 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 186; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.181 — Dòng 187: `trace_id=trace_id,`

```python
                        trace_id=trace_id,
```

**Nhãn:** L187

**Mô tả:** Hành vi dòng 187.

**Vị trí file:** `pipeline.py` dòng 187 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 187; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.182 — Dòng 188: `analysis_id=workflow.active_analysis_id or trace_id,`

```python
                        analysis_id=workflow.active_analysis_id or trace_id,
```

**Nhãn:** L188

**Mô tả:** Hành vi dòng 188.

**Vị trí file:** `pipeline.py` dòng 188 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 188; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.183 — Dòng 189: `step_type=WorkflowStepType.CLARIFY,`

```python
                        step_type=WorkflowStepType.CLARIFY,
```

**Nhãn:** L189

**Mô tả:** Hành vi dòng 189.

**Vị trí file:** `pipeline.py` dòng 189 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 189; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.184 — Dòng 190: `sql_attempt=sql_attempt,`

```python
                        sql_attempt=sql_attempt,
```

**Nhãn:** L190

**Mô tả:** Hành vi dòng 190.

**Vị trí file:** `pipeline.py` dòng 190 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 190; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.185 — Dòng 191: `summary=ii_parsed.clarification_request.get("reason", "clari...`

```python
                        summary=ii_parsed.clarification_request.get("reason", "clarify") if ii_parsed.clarification_request else "clarify",
```

**Nhãn:** L191

**Mô tả:** Hành vi dòng 191.

**Vị trí file:** `pipeline.py` dòng 191 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 191; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.186 — Dòng 192: `)`

```python
                    )
```

**Nhãn:** L192

**Mô tả:** Hành vi dòng 192.

**Vị trí file:** `pipeline.py` dòng 192 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 192; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.187 — Dòng 193: `)`

```python
                )
```

**Nhãn:** L193

**Mô tả:** Hành vi dòng 193.

**Vị trí file:** `pipeline.py` dòng 193 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 193; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.188 — Dòng 194: `if workflow.clarify_round > self.cfg.pipeline.max_clarify_ro...`

```python
                if workflow.clarify_round > self.cfg.pipeline.max_clarify_rounds:
```

**Nhãn:** max clarify

**Mô tả:** clarify_round > max_clarify_rounds.

**Vị trí file:** `pipeline.py` dòng 194 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 194; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.189 — Dòng 195: `if brief.user_knowledge_level == "unknown":`

```python
                    if brief.user_knowledge_level == "unknown":
```

**Nhãn:** L195

**Mô tả:** Hành vi dòng 195.

**Vị trí file:** `pipeline.py` dòng 195 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 195; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.190 — Dòng 196: `brief.exploration_mode = True`

```python
                        brief.exploration_mode = True
```

**Nhãn:** exploration_mode

**Mô tả:** unknown knowledge → exploration_mode True.

**Vị trí file:** `pipeline.py` dòng 196 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 196; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.191 — Dòng 197: `else:`

```python
                    else:
```

**Nhãn:** L197

**Mô tả:** Hành vi dòng 197.

**Vị trí file:** `pipeline.py` dòng 197 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 197; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.192 — Dòng 198: `raise ClarifyRoundsExceededError("Max clarification rounds e...`

```python
                        raise ClarifyRoundsExceededError("Max clarification rounds exceeded")
```

**Nhãn:** raise clarify exceeded

**Mô tả:** ClarifyRoundsExceededError — orchestrator catch.

**Vị trí file:** `pipeline.py` dòng 198 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 198; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.193 — Dòng 199: `else:`

```python
                else:
```

**Nhãn:** L199

**Mô tả:** Hành vi dòng 199.

**Vị trí file:** `pipeline.py` dòng 199 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 199; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.194 — Dòng 200: `needs_clarification = ClarificationRequest.model_validate(ii...`

```python
                    needs_clarification = ClarificationRequest.model_validate(ii_parsed.clarification_request)
```

**Nhãn:** ClarificationRequest

**Mô tả:** Validate và return NEEDS_CLARIFICATION.

**Vị trí file:** `pipeline.py` dòng 200 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 200; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.195 — Dòng 201: `workflow.status = WorkflowStatus.AWAITING_CLARIFICATION`

```python
                    workflow.status = WorkflowStatus.AWAITING_CLARIFICATION
```

**Nhãn:** L201

**Mô tả:** Hành vi dòng 201.

**Vị trí file:** `pipeline.py` dòng 201 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 201; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.196 — Dòng 202: `return PipelineResult(`

```python
                    return PipelineResult(
```

**Nhãn:** L202

**Mô tả:** Hành vi dòng 202.

**Vị trí file:** `pipeline.py` dòng 202 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 202; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.197 — Dòng 203: `trace_id=trace_id,`

```python
                        trace_id=trace_id,
```

**Nhãn:** L203

**Mô tả:** Hành vi dòng 203.

**Vị trí file:** `pipeline.py` dòng 203 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 203; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.198 — Dòng 204: `analysis_id=workflow.active_analysis_id or trace_id,`

```python
                        analysis_id=workflow.active_analysis_id or trace_id,
```

**Nhãn:** L204

**Mô tả:** Hành vi dòng 204.

**Vị trí file:** `pipeline.py` dòng 204 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 204; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.199 — Dòng 205: `outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value,`

```python
                        outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value,
```

**Nhãn:** L205

**Mô tả:** Hành vi dòng 205.

**Vị trí file:** `pipeline.py` dòng 205 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 205; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.200 — Dòng 206: `technical_summary=TechnicalSummary(outcome=AnalysisOutcome.N...`

```python
                        technical_summary=TechnicalSummary(outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value),
```

**Nhãn:** L206

**Mô tả:** Hành vi dòng 206.

**Vị trí file:** `pipeline.py` dòng 206 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 206; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.201 — Dòng 207: `workflow_steps=workflow.steps,`

```python
                        workflow_steps=workflow.steps,
```

**Nhãn:** L207

**Mô tả:** Hành vi dòng 207.

**Vị trí file:** `pipeline.py` dòng 207 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 207; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.202 — Dòng 208: `needs_clarification=needs_clarification,`

```python
                        needs_clarification=needs_clarification,
```

**Nhãn:** L208

**Mô tả:** Hành vi dòng 208.

**Vị trí file:** `pipeline.py` dòng 208 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 208; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.203 — Dòng 209: `)`

```python
                    )
```

**Nhãn:** L209

**Mô tả:** Hành vi dòng 209.

**Vị trí file:** `pipeline.py` dòng 209 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 209; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.204 — Dòng 210: ``

```python

```

**Nhãn:** L210

**Mô tả:** Hành vi dòng 210.

**Vị trí file:** `pipeline.py` dòng 210 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 210; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.205 — Dòng 211: `if action == "impossible":`

```python
            if action == "impossible":
```

**Nhãn:** impossible II

**Mô tả:** action impossible → _finish IMPOSSIBLE.

**Vị trí file:** `pipeline.py` dòng 211 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 211; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.206 — Dòng 212: `return self._finish(`

```python
                return self._finish(
```

**Nhãn:** L212

**Mô tả:** Hành vi dòng 212.

**_finish:** workflow IDLE, last_outcome, PipelineResult không needs_clarification.

**Vị trí file:** `pipeline.py` dòng 212 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 212; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.207 — Dòng 213: `trace_id,`

```python
                    trace_id,
```

**Nhãn:** L213

**Mô tả:** Hành vi dòng 213.

**Vị trí file:** `pipeline.py` dòng 213 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 213; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.208 — Dòng 214: `workflow,`

```python
                    workflow,
```

**Nhãn:** L214

**Mô tả:** Hành vi dòng 214.

**Vị trí file:** `pipeline.py` dòng 214 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 214; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.209 — Dòng 215: `AnalysisOutcome.IMPOSSIBLE,`

```python
                    AnalysisOutcome.IMPOSSIBLE,
```

**Nhãn:** L215

**Mô tả:** Hành vi dòng 215.

**Vị trí file:** `pipeline.py` dòng 215 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 215; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.210 — Dòng 216: `TechnicalSummary(`

```python
                    TechnicalSummary(
```

**Nhãn:** L216

**Mô tả:** Hành vi dòng 216.

**Vị trí file:** `pipeline.py` dòng 216 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 216; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.211 — Dòng 217: `outcome=AnalysisOutcome.IMPOSSIBLE.value,`

```python
                        outcome=AnalysisOutcome.IMPOSSIBLE.value,
```

**Nhãn:** L217

**Mô tả:** Hành vi dòng 217.

**Vị trí file:** `pipeline.py` dòng 217 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 217; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.212 — Dòng 218: `caveats=[ii_parsed.reason or ""],`

```python
                        caveats=[ii_parsed.reason or ""],
```

**Nhãn:** L218

**Mô tả:** Hành vi dòng 218.

**Vị trí file:** `pipeline.py` dòng 218 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 218; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.213 — Dòng 219: `),`

```python
                    ),
```

**Nhãn:** L219

**Mô tả:** Hành vi dòng 219.

**Vị trí file:** `pipeline.py` dòng 219 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 219; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.214 — Dòng 220: `)`

```python
                )
```

**Nhãn:** L220

**Mô tả:** Hành vi dòng 220.

**Vị trí file:** `pipeline.py` dòng 220 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 220; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.215 — Dòng 221: ``

```python

```

**Nhãn:** L221

**Mô tả:** Hành vi dòng 221.

**Vị trí file:** `pipeline.py` dòng 221 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 221; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.216 — Dòng 222: `if action not in {"plan_sql", "probe_sql"}:`

```python
            if action not in {"plan_sql", "probe_sql"}:
```

**Nhãn:** unknown action

**Mô tả:** action not in plan_sql probe_sql → continue.

**Vị trí file:** `pipeline.py` dòng 222 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 222; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.217 — Dòng 223: `continue`

```python
                continue
```

**Nhãn:** L223

**Mô tả:** Hành vi dòng 223.

**continue:** Bỏ phần còn lại vòng lặp hiện tại — sql_attempt hoặc query idx tiếp.

**Vị trí file:** `pipeline.py` dòng 223 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 223; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.218 — Dòng 224: ``

```python

```

**Nhãn:** L224

**Mô tả:** Hành vi dòng 224.

**Vị trí file:** `pipeline.py` dòng 224 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 224; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.219 — Dòng 225: `sql_queries: list[str] = list(ii_parsed.sql_queries)`

```python
            sql_queries: list[str] = list(ii_parsed.sql_queries)
```

**Nhãn:** L225

**Mô tả:** Hành vi dòng 225.

**Vị trí file:** `pipeline.py` dòng 225 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 225; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.220 — Dòng 226: `query_meta: list[dict[str, Any]] = list(ii_parsed.query_meta...`

```python
            query_meta: list[dict[str, Any]] = list(ii_parsed.query_meta)
```

**Nhãn:** L226

**Mô tả:** Hành vi dòng 226.

**Vị trí file:** `pipeline.py` dòng 226 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 226; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.221 — Dòng 227: `target_dbs: list[str] = list(ii_parsed.target_dbs)`

```python
            target_dbs: list[str] = list(ii_parsed.target_dbs)
```

**Nhãn:** L227

**Mô tả:** Hành vi dòng 227.

**Vị trí file:** `pipeline.py` dòng 227 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 227; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.222 — Dòng 228: `default_db = ii_parsed.target_db or "db2"`

```python
            default_db = ii_parsed.target_db or "db2"
```

**Nhãn:** L228

**Mô tả:** Hành vi dòng 228.

**Vị trí file:** `pipeline.py` dòng 228 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 228; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.223 — Dòng 229: ``

```python

```

**Nhãn:** L229

**Mô tả:** Hành vi dòng 229.

**Vị trí file:** `pipeline.py` dòng 229 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 229; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.224 — Dòng 230: `profiles: list[ResultProfile] = []`

```python
            profiles: list[ResultProfile] = []
```

**Nhãn:** L230

**Mô tả:** Hành vi dòng 230.

**Vị trí file:** `pipeline.py` dòng 230 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 230; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.225 — Dòng 231: `query_files: list[QueryResultFile] = []`

```python
            query_files: list[QueryResultFile] = []
```

**Nhãn:** L231

**Mô tả:** Hành vi dòng 231.

**Vị trí file:** `pipeline.py` dòng 231 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 231; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.226 — Dòng 232: `approved_sql: list[str] = []`

```python
            approved_sql: list[str] = []
```

**Nhãn:** L232

**Mô tả:** Hành vi dòng 232.

**Vị trí file:** `pipeline.py` dòng 232 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 232; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.227 — Dòng 233: `max_queries = self.cfg.pipeline.max_sql_queries_per_plan`

```python
            max_queries = self.cfg.pipeline.max_sql_queries_per_plan
```

**Nhãn:** L233

**Mô tả:** Hành vi dòng 233.

**Vị trí file:** `pipeline.py` dòng 233 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 233; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.228 — Dòng 234: `if action == "probe_sql":`

```python
            if action == "probe_sql":
```

**Nhãn:** probe cap

**Mô tả:** max_queries min 3 nếu probe_sql.

**Vị trí file:** `pipeline.py` dòng 234 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 234; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.229 — Dòng 235: `max_queries = min(max_queries, 3)`

```python
                max_queries = min(max_queries, 3)
```

**Nhãn:** L235

**Mô tả:** Hành vi dòng 235.

**Vị trí file:** `pipeline.py` dòng 235 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 235; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.230 — Dòng 236: ``

```python

```

**Nhãn:** L236

**Mô tả:** Hành vi dòng 236.

**Vị trí file:** `pipeline.py` dòng 236 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 236; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.231 — Dòng 237: `for idx, sql in enumerate(sql_queries[:max_queries]):`

```python
            for idx, sql in enumerate(sql_queries[:max_queries]):
```

**Nhãn:** for sql

**Mô tả:** enumerate sql_queries[:max_queries].

**Vị trí file:** `pipeline.py` dòng 237 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 237; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.232 — Dòng 238: `tdb = target_dbs[idx] if idx < len(target_dbs) else default_...`

```python
                tdb = target_dbs[idx] if idx < len(target_dbs) else default_db
```

**Nhãn:** L238

**Mô tả:** Hành vi dòng 238.

**Vị trí file:** `pipeline.py` dòng 238 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 238; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.233 — Dòng 239: `verdict = policy.validate(sql)`

```python
                verdict = policy.validate(sql)
```

**Nhãn:** policy validate

**Mô tả:** verdict = policy.validate sql.

**Vị trí file:** `pipeline.py` dòng 239 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 239; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.234 — Dòng 240: `if not verdict.allowed:`

```python
                if not verdict.allowed:
```

**Nhãn:** L240

**Mô tả:** Hành vi dòng 240.

**Vị trí file:** `pipeline.py` dòng 240 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 240; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.235 — Dòng 241: `workflow.progress_step = WorkflowStepType.POLICY_REJECT.valu...`

```python
                    workflow.progress_step = WorkflowStepType.POLICY_REJECT.value
```

**Nhãn:** L241

**Mô tả:** Hành vi dòng 241.

**Vị trí file:** `pipeline.py` dòng 241 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 241; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.236 — Dòng 242: `self._emit_progress(workflow, on_progress)`

```python
                    self._emit_progress(workflow, on_progress)
```

**Nhãn:** L242

**Mô tả:** Hành vi dòng 242.

**Vị trí file:** `pipeline.py` dòng 242 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 242; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.237 — Dòng 243: `workflow.steps.append(`

```python
                    workflow.steps.append(
```

**Nhãn:** L243

**Mô tả:** Hành vi dòng 243.

**Vị trí file:** `pipeline.py` dòng 243 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 243; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.238 — Dòng 244: `WorkflowStep(`

```python
                        WorkflowStep(
```

**Nhãn:** L244

**Mô tả:** Hành vi dòng 244.

**WorkflowStep:** step_id UUID mới; orchestrator persist workflow qua Redis sau run.

**Vị trí file:** `pipeline.py` dòng 244 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 244; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.239 — Dòng 245: `step_id=str(uuid4()),`

```python
                            step_id=str(uuid4()),
```

**Nhãn:** L245

**Mô tả:** Hành vi dòng 245.

**Vị trí file:** `pipeline.py` dòng 245 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 245; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.240 — Dòng 246: `trace_id=trace_id,`

```python
                            trace_id=trace_id,
```

**Nhãn:** L246

**Mô tả:** Hành vi dòng 246.

**Vị trí file:** `pipeline.py` dòng 246 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 246; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.241 — Dòng 247: `analysis_id=workflow.active_analysis_id or trace_id,`

```python
                            analysis_id=workflow.active_analysis_id or trace_id,
```

**Nhãn:** L247

**Mô tả:** Hành vi dòng 247.

**Vị trí file:** `pipeline.py` dòng 247 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 247; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.242 — Dòng 248: `step_type=WorkflowStepType.POLICY_REJECT,`

```python
                            step_type=WorkflowStepType.POLICY_REJECT,
```

**Nhãn:** L248

**Mô tả:** Hành vi dòng 248.

**Vị trí file:** `pipeline.py` dòng 248 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 248; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.243 — Dòng 249: `sql_attempt=sql_attempt,`

```python
                            sql_attempt=sql_attempt,
```

**Nhãn:** L249

**Mô tả:** Hành vi dòng 249.

**Vị trí file:** `pipeline.py` dòng 249 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 249; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.244 — Dòng 250: `query_index=idx,`

```python
                            query_index=idx,
```

**Nhãn:** L250

**Mô tả:** Hành vi dòng 250.

**Vị trí file:** `pipeline.py` dòng 250 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 250; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.245 — Dòng 251: `summary=";".join(verdict.violations),`

```python
                            summary=";".join(verdict.violations),
```

**Nhãn:** L251

**Mô tả:** Hành vi dòng 251.

**Vị trí file:** `pipeline.py` dòng 251 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 251; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.246 — Dòng 252: `)`

```python
                        )
```

**Nhãn:** L252

**Mô tả:** Hành vi dòng 252.

**Vị trí file:** `pipeline.py` dòng 252 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 252; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.247 — Dòng 253: `)`

```python
                    )
```

**Nhãn:** L253

**Mô tả:** Hành vi dòng 253.

**Vị trí file:** `pipeline.py` dòng 253 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 253; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.248 — Dòng 254: `inbox["policy_feedback"] = {"violations": verdict.violations...`

```python
                    inbox["policy_feedback"] = {"violations": verdict.violations, "query_index": idx}
```

**Nhãn:** L254

**Mô tả:** Hành vi dòng 254.

**Inbox:** Agent sau trong cùng run đọc qua payload — II nhận full inbox 156.

**Vị trí file:** `pipeline.py` dòng 254 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 254; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.249 — Dòng 255: `continue`

```python
                    continue
```

**Nhãn:** L255

**Mô tả:** Hành vi dòng 255.

**continue:** Bỏ phần còn lại vòng lặp hiện tại — sql_attempt hoặc query idx tiếp.

**Vị trí file:** `pipeline.py` dòng 255 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 255; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.250 — Dòng 256: ``

```python

```

**Nhãn:** L256

**Mô tả:** Hành vi dòng 256.

**Vị trí file:** `pipeline.py` dòng 256 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 256; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.251 — Dòng 257: `sanitized = verdict.sanitized_sql or sql`

```python
                sanitized = verdict.sanitized_sql or sql
```

**Nhãn:** sanitized

**Mô tả:** verdict.sanitized_sql or sql.

**Vị trí file:** `pipeline.py` dòng 257 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 257; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.252 — Dòng 258: `approved = False`

```python
                approved = False
```

**Nhãn:** L258

**Mô tả:** Hành vi dòng 258.

**Vị trí file:** `pipeline.py` dòng 258 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 258; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.253 — Dòng 259: `explain_attached = False`

```python
                explain_attached = False
```

**Nhãn:** L259

**Mô tả:** Hành vi dòng 259.

**Vị trí file:** `pipeline.py` dòng 259 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 259; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.254 — Dòng 260: `for risk_attempt in range(1, self.cfg.pipeline.max_risk_retr...`

```python
                for risk_attempt in range(1, self.cfg.pipeline.max_risk_retries + 1):
```

**Nhãn:** risk loop

**Mô tả:** for risk_attempt max_risk_retries.

**Vị trí file:** `pipeline.py` dòng 260 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 260; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.255 — Dòng 261: `budget.record("III")`

```python
                    budget.record("III")
```

**Nhãn:** L261

**Mô tả:** Hành vi dòng 261.

**Vị trí file:** `pipeline.py` dòng 261 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 261; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.256 — Dòng 262: `iii_raw = self.agent_invoker.invoke(`

```python
                    iii_raw = self.agent_invoker.invoke(
```

**Nhãn:** L262

**Mô tả:** Hành vi dòng 262.

**Invoke agent:** Payload dict; metadata mode plan_sql/review/analyze. Lỗi HTTP propagate — pipeline không catch network.

**Vị trí file:** `pipeline.py` dòng 262 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 262; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.257 — Dòng 263: `"III",`

```python
                        "III",
```

**Nhãn:** L263

**Mô tả:** Hành vi dòng 263.

**Vị trí file:** `pipeline.py` dòng 263 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 263; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.258 — Dòng 264: `{`

```python
                        {
```

**Nhãn:** L264

**Mô tả:** Hành vi dòng 264.

**Vị trí file:** `pipeline.py` dòng 264 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 264; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.259 — Dòng 265: `"sql": sanitized,`

```python
                            "sql": sanitized,
```

**Nhãn:** L265

**Mô tả:** Hành vi dòng 265.

**Vị trí file:** `pipeline.py` dòng 265 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 265; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.260 — Dòng 266: `"intent_slice": brief.model_dump(),`

```python
                            "intent_slice": brief.model_dump(),
```

**Nhãn:** L266

**Mô tả:** Hành vi dòng 266.

**model_dump:** JSON-serializable cho HTTP agent; permissions dùng mode="json".

**Vị trí file:** `pipeline.py` dòng 266 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 266; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.261 — Dòng 267: `"risk_attempt": risk_attempt,`

```python
                            "risk_attempt": risk_attempt,
```

**Nhãn:** L267

**Mô tả:** Hành vi dòng 267.

**Vị trí file:** `pipeline.py` dòng 267 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 267; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.262 — Dòng 268: `"schema_context": schema_context,`

```python
                            "schema_context": schema_context,
```

**Nhãn:** L268

**Mô tả:** Hành vi dòng 268.

**Vị trí file:** `pipeline.py` dòng 268 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 268; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.263 — Dòng 269: `"allowed_tables": permissions.allowed_tables,`

```python
                            "allowed_tables": permissions.allowed_tables,
```

**Nhãn:** L269

**Mô tả:** Hành vi dòng 269.

**Vị trí file:** `pipeline.py` dòng 269 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 269; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.264 — Dòng 270: `"denied_columns": permissions.denied_columns,`

```python
                            "denied_columns": permissions.denied_columns,
```

**Nhãn:** L270

**Mô tả:** Hành vi dòng 270.

**Vị trí file:** `pipeline.py` dòng 270 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 270; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.265 — Dòng 271: `"store_ids": permissions.store_ids,`

```python
                            "store_ids": permissions.store_ids,
```

**Nhãn:** L271

**Mô tả:** Hành vi dòng 271.

**Vị trí file:** `pipeline.py` dòng 271 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 271; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.266 — Dòng 272: `"store_filter_required": permissions.store_filter_required,`

```python
                            "store_filter_required": permissions.store_filter_required,
```

**Nhãn:** L272

**Mô tả:** Hành vi dòng 272.

**Vị trí file:** `pipeline.py` dòng 272 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 272; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.267 — Dòng 273: `"explain_plan": inbox.get("explain_plan"),`

```python
                            "explain_plan": inbox.get("explain_plan"),
```

**Nhãn:** L273

**Mô tả:** Hành vi dòng 273.

**Vị trí file:** `pipeline.py` dòng 273 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 273; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.268 — Dòng 274: `"permissions": permissions.model_dump(mode="json"),`

```python
                            "permissions": permissions.model_dump(mode="json"),
```

**Nhãn:** L274

**Mô tả:** Hành vi dòng 274.

**model_dump:** JSON-serializable cho HTTP agent; permissions dùng mode="json".

**Vị trí file:** `pipeline.py` dòng 274 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 274; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.269 — Dòng 275: `},`

```python
                        },
```

**Nhãn:** L275

**Mô tả:** Hành vi dòng 275.

**Vị trí file:** `pipeline.py` dòng 275 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 275; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.270 — Dòng 276: `{"mode": "review"},`

```python
                        {"mode": "review"},
```

**Nhãn:** L276

**Mô tả:** Hành vi dòng 276.

**Vị trí file:** `pipeline.py` dòng 276 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 276; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.271 — Dòng 277: `)`

```python
                    )
```

**Nhãn:** L277

**Mô tả:** Hành vi dòng 277.

**Vị trí file:** `pipeline.py` dòng 277 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 277; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.272 — Dòng 278: `try:`

```python
                    try:
```

**Nhãn:** L278

**Mô tả:** Hành vi dòng 278.

**Vị trí file:** `pipeline.py` dòng 278 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 278; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.273 — Dòng 279: `iii_parsed = parse_agent_response("III", iii_raw)`

```python
                        iii_parsed = parse_agent_response("III", iii_raw)
```

**Nhãn:** L279

**Mô tả:** Hành vi dòng 279.

**Vị trí file:** `pipeline.py` dòng 279 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 279; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.274 — Dòng 280: `except ContractInvalidError as exc:`

```python
                    except ContractInvalidError as exc:
```

**Nhãn:** L280

**Mô tả:** Hành vi dòng 280.

**Vị trí file:** `pipeline.py` dòng 280 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 280; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.275 — Dòng 281: `return self._finish(`

```python
                        return self._finish(
```

**Nhãn:** L281

**Mô tả:** Hành vi dòng 281.

**_finish:** workflow IDLE, last_outcome, PipelineResult không needs_clarification.

**Vị trí file:** `pipeline.py` dòng 281 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 281; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.276 — Dòng 282: `trace_id,`

```python
                            trace_id,
```

**Nhãn:** L282

**Mô tả:** Hành vi dòng 282.

**Vị trí file:** `pipeline.py` dòng 282 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 282; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.277 — Dòng 283: `workflow,`

```python
                            workflow,
```

**Nhãn:** L283

**Mô tả:** Hành vi dòng 283.

**Vị trí file:** `pipeline.py` dòng 283 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 283; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.278 — Dòng 284: `AnalysisOutcome.ERROR,`

```python
                            AnalysisOutcome.ERROR,
```

**Nhãn:** L284

**Mô tả:** Hành vi dòng 284.

**Vị trí file:** `pipeline.py` dòng 284 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 284; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.279 — Dòng 285: `TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveat...`

```python
                            TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveats=[str(exc)]),
```

**Nhãn:** L285

**Mô tả:** Hành vi dòng 285.

**Vị trí file:** `pipeline.py` dòng 285 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 285; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.280 — Dòng 286: `)`

```python
                        )
```

**Nhãn:** L286

**Mô tả:** Hành vi dòng 286.

**Vị trí file:** `pipeline.py` dòng 286 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 286; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.281 — Dòng 287: `if not isinstance(iii_parsed, RiskReviewResponse):`

```python
                    if not isinstance(iii_parsed, RiskReviewResponse):
```

**Nhãn:** L287

**Mô tả:** Hành vi dòng 287.

**Vị trí file:** `pipeline.py` dòng 287 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 287; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.282 — Dòng 288: `return self._finish(`

```python
                        return self._finish(
```

**Nhãn:** L288

**Mô tả:** Hành vi dòng 288.

**_finish:** workflow IDLE, last_outcome, PipelineResult không needs_clarification.

**Vị trí file:** `pipeline.py` dòng 288 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 288; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.283 — Dòng 289: `trace_id,`

```python
                            trace_id,
```

**Nhãn:** L289

**Mô tả:** Hành vi dòng 289.

**Vị trí file:** `pipeline.py` dòng 289 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 289; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.284 — Dòng 290: `workflow,`

```python
                            workflow,
```

**Nhãn:** L290

**Mô tả:** Hành vi dòng 290.

**Vị trí file:** `pipeline.py` dòng 290 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 290; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.285 — Dòng 291: `AnalysisOutcome.ERROR,`

```python
                            AnalysisOutcome.ERROR,
```

**Nhãn:** L291

**Mô tả:** Hành vi dòng 291.

**Vị trí file:** `pipeline.py` dòng 291 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 291; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.286 — Dòng 292: `TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveat...`

```python
                            TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveats=["invalid_agent_iii"]),
```

**Nhãn:** L292

**Mô tả:** Hành vi dòng 292.

**Vị trí file:** `pipeline.py` dòng 292 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 292; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.287 — Dòng 293: `)`

```python
                        )
```

**Nhãn:** L293

**Mô tả:** Hành vi dòng 293.

**Vị trí file:** `pipeline.py` dòng 293 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 293; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.288 — Dòng 294: `if iii_parsed.verdict == "approve":`

```python
                    if iii_parsed.verdict == "approve":
```

**Nhãn:** approve III

**Mô tả:** verdict approve break.

**Vị trí file:** `pipeline.py` dòng 294 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 294; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.289 — Dòng 295: `approved = True`

```python
                        approved = True
```

**Nhãn:** L295

**Mô tả:** Hành vi dòng 295.

**Vị trí file:** `pipeline.py` dòng 295 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 295; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.290 — Dòng 296: `break`

```python
                        break
```

**Nhãn:** L296

**Mô tả:** Hành vi dòng 296.

**Vị trí file:** `pipeline.py` dòng 296 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 296; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.291 — Dòng 297: `inbox["risk_feedback"] = iii_parsed.risk_feedback`

```python
                    inbox["risk_feedback"] = iii_parsed.risk_feedback
```

**Nhãn:** L297

**Mô tả:** Hành vi dòng 297.

**Inbox:** Agent sau trong cùng run đọc qua payload — II nhận full inbox 156.

**Vị trí file:** `pipeline.py` dòng 297 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 297; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.292 — Dòng 298: `if not explain_attached and (`

```python
                    if not explain_attached and (
```

**Nhãn:** L298

**Mô tả:** Hành vi dòng 298.

**Vị trí file:** `pipeline.py` dòng 298 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 298; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.293 — Dòng 299: `iii_parsed.needs_explain`

```python
                        iii_parsed.needs_explain
```

**Nhãn:** L299

**Mô tả:** Hành vi dòng 299.

**Vị trí file:** `pipeline.py` dòng 299 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 299; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.294 — Dòng 300: `or _needs_explain_from_feedback(iii_parsed.risk_feedback)`

```python
                        or _needs_explain_from_feedback(iii_parsed.risk_feedback)
```

**Nhãn:** L300

**Mô tả:** Hành vi dòng 300.

**Vị trí file:** `pipeline.py` dòng 300 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 300; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.295 — Dòng 301: `):`

```python
                    ):
```

**Nhãn:** L301

**Mô tả:** Hành vi dòng 301.

**Vị trí file:** `pipeline.py` dòng 301 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 301; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.296 — Dòng 302: `if self.context_policy.can_invoke_tool(permissions, "III", "...`

```python
                        if self.context_policy.can_invoke_tool(permissions, "III", "explain_sql"):
```

**Nhãn:** L302

**Mô tả:** Hành vi dòng 302.

**ContextPolicy:** Gate quyền tool/function/SQL — POLICY_BLOCKED nếu thiếu grant.

**Vị trí file:** `pipeline.py` dòng 302 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 302; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.297 — Dòng 303: `explain_result = self.sql_gateway.explain_sql(sanitized, acl...`

```python
                            explain_result = self.sql_gateway.explain_sql(sanitized, acl, target_db=tdb)
```

**Nhãn:** explain_sql

**Mô tả:** sql_gateway.explain_sql nếu có quyền.

**Vị trí file:** `pipeline.py` dòng 303 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 303; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.298 — Dòng 304: `inbox["explain_plan"] = explain_result`

```python
                            inbox["explain_plan"] = explain_result
```

**Nhãn:** L304

**Mô tả:** Hành vi dòng 304.

**Inbox:** Agent sau trong cùng run đọc qua payload — II nhận full inbox 156.

**Vị trí file:** `pipeline.py` dòng 304 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 304; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.299 — Dòng 305: `self.audit.log_sql_explain(`

```python
                            self.audit.log_sql_explain(
```

**Nhãn:** L305

**Mô tả:** Hành vi dòng 305.

**Audit:** Ghi explain/execute cho compliance — trace_id, actor_id, sql, outcome.

**Vị trí file:** `pipeline.py` dòng 305 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 305; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.300 — Dòng 306: `trace_id=trace_id,`

```python
                                trace_id=trace_id,
```

**Nhãn:** L306

**Mô tả:** Hành vi dòng 306.

**Vị trí file:** `pipeline.py` dòng 306 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 306; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.301 — Dòng 307: `actor_id=acl.actor_id,`

```python
                                actor_id=acl.actor_id,
```

**Nhãn:** L307

**Mô tả:** Hành vi dòng 307.

**Vị trí file:** `pipeline.py` dòng 307 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 307; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.302 — Dòng 308: `sql=sanitized,`

```python
                                sql=sanitized,
```

**Nhãn:** L308

**Mô tả:** Hành vi dòng 308.

**Vị trí file:** `pipeline.py` dòng 308 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 308; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.303 — Dòng 309: `target_db=tdb,`

```python
                                target_db=tdb,
```

**Nhãn:** L309

**Mô tả:** Hành vi dòng 309.

**Vị trí file:** `pipeline.py` dòng 309 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 309; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.304 — Dòng 310: `outcome=str(explain_result.get("status", "unknown")),`

```python
                                outcome=str(explain_result.get("status", "unknown")),
```

**Nhãn:** L310

**Mô tả:** Hành vi dòng 310.

**Vị trí file:** `pipeline.py` dòng 310 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 310; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.305 — Dòng 311: `violations=explain_result.get("violations"),`

```python
                                violations=explain_result.get("violations"),
```

**Nhãn:** L311

**Mô tả:** Hành vi dòng 311.

**Vị trí file:** `pipeline.py` dòng 311 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 311; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.306 — Dòng 312: `)`

```python
                            )
```

**Nhãn:** L312

**Mô tả:** Hành vi dòng 312.

**Vị trí file:** `pipeline.py` dòng 312 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 312; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.307 — Dòng 313: `explain_attached = True`

```python
                            explain_attached = True
```

**Nhãn:** L313

**Mô tả:** Hành vi dòng 313.

**Vị trí file:** `pipeline.py` dòng 313 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 313; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.308 — Dòng 314: `else:`

```python
                        else:
```

**Nhãn:** L314

**Mô tả:** Hành vi dòng 314.

**Vị trí file:** `pipeline.py` dòng 314 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 314; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.309 — Dòng 315: `return self._finish(`

```python
                            return self._finish(
```

**Nhãn:** L315

**Mô tả:** Hành vi dòng 315.

**_finish:** workflow IDLE, last_outcome, PipelineResult không needs_clarification.

**Vị trí file:** `pipeline.py` dòng 315 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 315; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.310 — Dòng 316: `trace_id,`

```python
                                trace_id,
```

**Nhãn:** L316

**Mô tả:** Hành vi dòng 316.

**Vị trí file:** `pipeline.py` dòng 316 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 316; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.311 — Dòng 317: `workflow,`

```python
                                workflow,
```

**Nhãn:** L317

**Mô tả:** Hành vi dòng 317.

**Vị trí file:** `pipeline.py` dòng 317 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 317; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.312 — Dòng 318: `AnalysisOutcome.POLICY_BLOCKED,`

```python
                                AnalysisOutcome.POLICY_BLOCKED,
```

**Nhãn:** L318

**Mô tả:** Hành vi dòng 318.

**Vị trí file:** `pipeline.py` dòng 318 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 318; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.313 — Dòng 319: `TechnicalSummary(`

```python
                                TechnicalSummary(
```

**Nhãn:** L319

**Mô tả:** Hành vi dòng 319.

**Vị trí file:** `pipeline.py` dòng 319 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 319; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.314 — Dòng 320: `outcome=AnalysisOutcome.POLICY_BLOCKED.value,`

```python
                                    outcome=AnalysisOutcome.POLICY_BLOCKED.value,
```

**Nhãn:** L320

**Mô tả:** Hành vi dòng 320.

**Vị trí file:** `pipeline.py` dòng 320 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 320; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.315 — Dòng 321: `caveats=["explain_sql not granted"],`

```python
                                    caveats=["explain_sql not granted"],
```

**Nhãn:** L321

**Mô tả:** Hành vi dòng 321.

**Vị trí file:** `pipeline.py` dòng 321 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 321; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.316 — Dòng 322: `),`

```python
                                ),
```

**Nhãn:** L322

**Mô tả:** Hành vi dòng 322.

**Vị trí file:** `pipeline.py` dòng 322 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 322; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.317 — Dòng 323: `)`

```python
                            )
```

**Nhãn:** L323

**Mô tả:** Hành vi dòng 323.

**Vị trí file:** `pipeline.py` dòng 323 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 323; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.318 — Dòng 324: ``

```python

```

**Nhãn:** L324

**Mô tả:** Hành vi dòng 324.

**Vị trí file:** `pipeline.py` dòng 324 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 324; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.319 — Dòng 325: `if not approved:`

```python
                if not approved:
```

**Nhãn:** L325

**Mô tả:** Hành vi dòng 325.

**Vị trí file:** `pipeline.py` dòng 325 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 325; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.320 — Dòng 326: `workflow.steps.append(`

```python
                    workflow.steps.append(
```

**Nhãn:** L326

**Mô tả:** Hành vi dòng 326.

**Vị trí file:** `pipeline.py` dòng 326 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 326; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.321 — Dòng 327: `WorkflowStep(`

```python
                        WorkflowStep(
```

**Nhãn:** L327

**Mô tả:** Hành vi dòng 327.

**WorkflowStep:** step_id UUID mới; orchestrator persist workflow qua Redis sau run.

**Vị trí file:** `pipeline.py` dòng 327 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 327; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.322 — Dòng 328: `step_id=str(uuid4()),`

```python
                            step_id=str(uuid4()),
```

**Nhãn:** L328

**Mô tả:** Hành vi dòng 328.

**Vị trí file:** `pipeline.py` dòng 328 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 328; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.323 — Dòng 329: `trace_id=trace_id,`

```python
                            trace_id=trace_id,
```

**Nhãn:** L329

**Mô tả:** Hành vi dòng 329.

**Vị trí file:** `pipeline.py` dòng 329 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 329; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.324 — Dòng 330: `analysis_id=workflow.active_analysis_id or trace_id,`

```python
                            analysis_id=workflow.active_analysis_id or trace_id,
```

**Nhãn:** L330

**Mô tả:** Hành vi dòng 330.

**Vị trí file:** `pipeline.py` dòng 330 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 330; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.325 — Dòng 331: `step_type=WorkflowStepType.RISK_REJECT,`

```python
                            step_type=WorkflowStepType.RISK_REJECT,
```

**Nhãn:** L331

**Mô tả:** Hành vi dòng 331.

**Vị trí file:** `pipeline.py` dòng 331 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 331; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.326 — Dòng 332: `sql_attempt=sql_attempt,`

```python
                            sql_attempt=sql_attempt,
```

**Nhãn:** L332

**Mô tả:** Hành vi dòng 332.

**Vị trí file:** `pipeline.py` dòng 332 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 332; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.327 — Dòng 333: `query_index=idx,`

```python
                            query_index=idx,
```

**Nhãn:** L333

**Mô tả:** Hành vi dòng 333.

**Vị trí file:** `pipeline.py` dòng 333 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 333; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.328 — Dòng 334: `summary="risk_reject",`

```python
                            summary="risk_reject",
```

**Nhãn:** L334

**Mô tả:** Hành vi dòng 334.

**Vị trí file:** `pipeline.py` dòng 334 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 334; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.329 — Dòng 335: `)`

```python
                        )
```

**Nhãn:** L335

**Mô tả:** Hành vi dòng 335.

**Vị trí file:** `pipeline.py` dòng 335 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 335; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.330 — Dòng 336: `)`

```python
                    )
```

**Nhãn:** L336

**Mô tả:** Hành vi dòng 336.

**Vị trí file:** `pipeline.py` dòng 336 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 336; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.331 — Dòng 337: `continue`

```python
                    continue
```

**Nhãn:** L337

**Mô tả:** Hành vi dòng 337.

**continue:** Bỏ phần còn lại vòng lặp hiện tại — sql_attempt hoặc query idx tiếp.

**Vị trí file:** `pipeline.py` dòng 337 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 337; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.332 — Dòng 338: ``

```python

```

**Nhãn:** L338

**Mô tả:** Hành vi dòng 338.

**Vị trí file:** `pipeline.py` dòng 338 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 338; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.333 — Dòng 339: `if not self.context_policy.can_invoke_tool(permissions, "II"...`

```python
                if not self.context_policy.can_invoke_tool(permissions, "II", "validate_sql"):
```

**Nhãn:** L339

**Mô tả:** Hành vi dòng 339.

**ContextPolicy:** Gate quyền tool/function/SQL — POLICY_BLOCKED nếu thiếu grant.

**Vị trí file:** `pipeline.py` dòng 339 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 339; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.334 — Dòng 340: `return self._finish(`

```python
                    return self._finish(
```

**Nhãn:** L340

**Mô tả:** Hành vi dòng 340.

**_finish:** workflow IDLE, last_outcome, PipelineResult không needs_clarification.

**Vị trí file:** `pipeline.py` dòng 340 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 340; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.335 — Dòng 341: `trace_id,`

```python
                        trace_id,
```

**Nhãn:** L341

**Mô tả:** Hành vi dòng 341.

**Vị trí file:** `pipeline.py` dòng 341 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 341; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.336 — Dòng 342: `workflow,`

```python
                        workflow,
```

**Nhãn:** L342

**Mô tả:** Hành vi dòng 342.

**Vị trí file:** `pipeline.py` dòng 342 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 342; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.337 — Dòng 343: `AnalysisOutcome.POLICY_BLOCKED,`

```python
                        AnalysisOutcome.POLICY_BLOCKED,
```

**Nhãn:** L343

**Mô tả:** Hành vi dòng 343.

**Vị trí file:** `pipeline.py` dòng 343 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 343; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.338 — Dòng 344: `TechnicalSummary(`

```python
                        TechnicalSummary(
```

**Nhãn:** L344

**Mô tả:** Hành vi dòng 344.

**Vị trí file:** `pipeline.py` dòng 344 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 344; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.339 — Dòng 345: `outcome=AnalysisOutcome.POLICY_BLOCKED.value,`

```python
                            outcome=AnalysisOutcome.POLICY_BLOCKED.value,
```

**Nhãn:** L345

**Mô tả:** Hành vi dòng 345.

**Vị trí file:** `pipeline.py` dòng 345 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 345; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.340 — Dòng 346: `caveats=["validate_sql not granted"],`

```python
                            caveats=["validate_sql not granted"],
```

**Nhãn:** L346

**Mô tả:** Hành vi dòng 346.

**Vị trí file:** `pipeline.py` dòng 346 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 346; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.341 — Dòng 347: `),`

```python
                        ),
```

**Nhãn:** L347

**Mô tả:** Hành vi dòng 347.

**Vị trí file:** `pipeline.py` dòng 347 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 347; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.342 — Dòng 348: `)`

```python
                    )
```

**Nhãn:** L348

**Mô tả:** Hành vi dòng 348.

**Vị trí file:** `pipeline.py` dòng 348 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 348; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.343 — Dòng 349: ``

```python

```

**Nhãn:** L349

**Mô tả:** Hành vi dòng 349.

**Vị trí file:** `pipeline.py` dòng 349 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 349; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.344 — Dòng 350: `if not self.context_policy.can_execute_sql(permissions):`

```python
                if not self.context_policy.can_execute_sql(permissions):
```

**Nhãn:** L350

**Mô tả:** Hành vi dòng 350.

**ContextPolicy:** Gate quyền tool/function/SQL — POLICY_BLOCKED nếu thiếu grant.

**Vị trí file:** `pipeline.py` dòng 350 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 350; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.345 — Dòng 351: `return self._finish(`

```python
                    return self._finish(
```

**Nhãn:** L351

**Mô tả:** Hành vi dòng 351.

**_finish:** workflow IDLE, last_outcome, PipelineResult không needs_clarification.

**Vị trí file:** `pipeline.py` dòng 351 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 351; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.346 — Dòng 352: `trace_id,`

```python
                        trace_id,
```

**Nhãn:** L352

**Mô tả:** Hành vi dòng 352.

**Vị trí file:** `pipeline.py` dòng 352 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 352; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.347 — Dòng 353: `workflow,`

```python
                        workflow,
```

**Nhãn:** L353

**Mô tả:** Hành vi dòng 353.

**Vị trí file:** `pipeline.py` dòng 353 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 353; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.348 — Dòng 354: `AnalysisOutcome.POLICY_BLOCKED,`

```python
                        AnalysisOutcome.POLICY_BLOCKED,
```

**Nhãn:** L354

**Mô tả:** Hành vi dòng 354.

**Vị trí file:** `pipeline.py` dòng 354 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 354; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.349 — Dòng 355: `TechnicalSummary(`

```python
                        TechnicalSummary(
```

**Nhãn:** L355

**Mô tả:** Hành vi dòng 355.

**Vị trí file:** `pipeline.py` dòng 355 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 355; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.350 — Dòng 356: `outcome=AnalysisOutcome.POLICY_BLOCKED.value,`

```python
                            outcome=AnalysisOutcome.POLICY_BLOCKED.value,
```

**Nhãn:** L356

**Mô tả:** Hành vi dòng 356.

**Vị trí file:** `pipeline.py` dòng 356 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 356; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.351 — Dòng 357: `caveats=["execute_readonly not granted"],`

```python
                            caveats=["execute_readonly not granted"],
```

**Nhãn:** L357

**Mô tả:** Hành vi dòng 357.

**Vị trí file:** `pipeline.py` dòng 357 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 357; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.352 — Dòng 358: `),`

```python
                        ),
```

**Nhãn:** L358

**Mô tả:** Hành vi dòng 358.

**Vị trí file:** `pipeline.py` dòng 358 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 358; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.353 — Dòng 359: `)`

```python
                    )
```

**Nhãn:** L359

**Mô tả:** Hành vi dòng 359.

**Vị trí file:** `pipeline.py` dòng 359 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 359; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.354 — Dòng 360: ``

```python

```

**Nhãn:** L360

**Mô tả:** Hành vi dòng 360.

**Vị trí file:** `pipeline.py` dòng 360 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 360; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.355 — Dòng 361: `workflow.progress_step = WorkflowStepType.EXECUTE.value`

```python
                workflow.progress_step = WorkflowStepType.EXECUTE.value
```

**Nhãn:** L361

**Mô tả:** Hành vi dòng 361.

**Vị trí file:** `pipeline.py` dòng 361 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 361; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.356 — Dòng 362: `self._emit_progress(workflow, on_progress)`

```python
                self._emit_progress(workflow, on_progress)
```

**Nhãn:** L362

**Mô tả:** Hành vi dòng 362.

**Vị trí file:** `pipeline.py` dòng 362 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 362; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.357 — Dòng 363: `exec_result = self.sql_gateway.execute_readonly(sanitized, a...`

```python
                exec_result = self.sql_gateway.execute_readonly(sanitized, acl, target_db=tdb)
```

**Nhãn:** execute

**Mô tả:** sql_gateway.execute_readonly.

**Vị trí file:** `pipeline.py` dòng 363 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 363; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.358 — Dòng 364: `if exec_result.get("error") == "policy_blocked":`

```python
                if exec_result.get("error") == "policy_blocked":
```

**Nhãn:** L364

**Mô tả:** Hành vi dòng 364.

**Vị trí file:** `pipeline.py` dòng 364 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 364; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.359 — Dòng 365: `self.audit.log_sql_execute(`

```python
                    self.audit.log_sql_execute(
```

**Nhãn:** L365

**Mô tả:** Hành vi dòng 365.

**Audit:** Ghi explain/execute cho compliance — trace_id, actor_id, sql, outcome.

**Vị trí file:** `pipeline.py` dòng 365 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 365; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.360 — Dòng 366: `trace_id=trace_id,`

```python
                        trace_id=trace_id,
```

**Nhãn:** L366

**Mô tả:** Hành vi dòng 366.

**Vị trí file:** `pipeline.py` dòng 366 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 366; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.361 — Dòng 367: `actor_id=acl.actor_id,`

```python
                        actor_id=acl.actor_id,
```

**Nhãn:** L367

**Mô tả:** Hành vi dòng 367.

**Vị trí file:** `pipeline.py` dòng 367 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 367; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.362 — Dòng 368: `role=acl.role,`

```python
                        role=acl.role,
```

**Nhãn:** L368

**Mô tả:** Hành vi dòng 368.

**Vị trí file:** `pipeline.py` dòng 368 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 368; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.363 — Dòng 369: `sql=sanitized,`

```python
                        sql=sanitized,
```

**Nhãn:** L369

**Mô tả:** Hành vi dòng 369.

**Vị trí file:** `pipeline.py` dòng 369 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 369; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.364 — Dòng 370: `target_db=tdb,`

```python
                        target_db=tdb,
```

**Nhãn:** L370

**Mô tả:** Hành vi dòng 370.

**Vị trí file:** `pipeline.py` dòng 370 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 370; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.365 — Dòng 371: `row_count=0,`

```python
                        row_count=0,
```

**Nhãn:** L371

**Mô tả:** Hành vi dòng 371.

**Vị trí file:** `pipeline.py` dòng 371 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 371; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.366 — Dòng 372: `outcome="policy_blocked",`

```python
                        outcome="policy_blocked",
```

**Nhãn:** L372

**Mô tả:** Hành vi dòng 372.

**Vị trí file:** `pipeline.py` dòng 372 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 372; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.367 — Dòng 373: `violations=exec_result.get("violations"),`

```python
                        violations=exec_result.get("violations"),
```

**Nhãn:** L373

**Mô tả:** Hành vi dòng 373.

**Vị trí file:** `pipeline.py` dòng 373 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 373; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.368 — Dòng 374: `)`

```python
                    )
```

**Nhãn:** L374

**Mô tả:** Hành vi dòng 374.

**Vị trí file:** `pipeline.py` dòng 374 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 374; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.369 — Dòng 375: `workflow.steps.append(`

```python
                    workflow.steps.append(
```

**Nhãn:** L375

**Mô tả:** Hành vi dòng 375.

**Vị trí file:** `pipeline.py` dòng 375 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 375; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.370 — Dòng 376: `WorkflowStep(`

```python
                        WorkflowStep(
```

**Nhãn:** L376

**Mô tả:** Hành vi dòng 376.

**WorkflowStep:** step_id UUID mới; orchestrator persist workflow qua Redis sau run.

**Vị trí file:** `pipeline.py` dòng 376 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 376; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.371 — Dòng 377: `step_id=str(uuid4()),`

```python
                            step_id=str(uuid4()),
```

**Nhãn:** L377

**Mô tả:** Hành vi dòng 377.

**Vị trí file:** `pipeline.py` dòng 377 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 377; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.372 — Dòng 378: `trace_id=trace_id,`

```python
                            trace_id=trace_id,
```

**Nhãn:** L378

**Mô tả:** Hành vi dòng 378.

**Vị trí file:** `pipeline.py` dòng 378 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 378; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.373 — Dòng 379: `analysis_id=workflow.active_analysis_id or trace_id,`

```python
                            analysis_id=workflow.active_analysis_id or trace_id,
```

**Nhãn:** L379

**Mô tả:** Hành vi dòng 379.

**Vị trí file:** `pipeline.py` dòng 379 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 379; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.374 — Dòng 380: `step_type=WorkflowStepType.POLICY_REJECT,`

```python
                            step_type=WorkflowStepType.POLICY_REJECT,
```

**Nhãn:** L380

**Mô tả:** Hành vi dòng 380.

**Vị trí file:** `pipeline.py` dòng 380 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 380; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.375 — Dòng 381: `sql_attempt=sql_attempt,`

```python
                            sql_attempt=sql_attempt,
```

**Nhãn:** L381

**Mô tả:** Hành vi dòng 381.

**Vị trí file:** `pipeline.py` dòng 381 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 381; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.376 — Dòng 382: `query_index=idx,`

```python
                            query_index=idx,
```

**Nhãn:** L382

**Mô tả:** Hành vi dòng 382.

**Vị trí file:** `pipeline.py` dòng 382 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 382; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.377 — Dòng 383: `summary="gateway_policy_blocked",`

```python
                            summary="gateway_policy_blocked",
```

**Nhãn:** L383

**Mô tả:** Hành vi dòng 383.

**Vị trí file:** `pipeline.py` dòng 383 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 383; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.378 — Dòng 384: `)`

```python
                        )
```

**Nhãn:** L384

**Mô tả:** Hành vi dòng 384.

**Vị trí file:** `pipeline.py` dòng 384 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 384; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.379 — Dòng 385: `)`

```python
                    )
```

**Nhãn:** L385

**Mô tả:** Hành vi dòng 385.

**Vị trí file:** `pipeline.py` dòng 385 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 385; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.380 — Dòng 386: `continue`

```python
                    continue
```

**Nhãn:** L386

**Mô tả:** Hành vi dòng 386.

**continue:** Bỏ phần còn lại vòng lặp hiện tại — sql_attempt hoặc query idx tiếp.

**Vị trí file:** `pipeline.py` dòng 386 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 386; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.381 — Dòng 387: `rows = exec_result.get("rows") or []`

```python
                rows = exec_result.get("rows") or []
```

**Nhãn:** L387

**Mô tả:** Hành vi dòng 387.

**Vị trí file:** `pipeline.py` dòng 387 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 387; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.382 — Dòng 388: `self.audit.log_sql_execute(`

```python
                self.audit.log_sql_execute(
```

**Nhãn:** L388

**Mô tả:** Hành vi dòng 388.

**Audit:** Ghi explain/execute cho compliance — trace_id, actor_id, sql, outcome.

**Vị trí file:** `pipeline.py` dòng 388 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 388; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.383 — Dòng 389: `trace_id=trace_id,`

```python
                    trace_id=trace_id,
```

**Nhãn:** L389

**Mô tả:** Hành vi dòng 389.

**Vị trí file:** `pipeline.py` dòng 389 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 389; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.384 — Dòng 390: `actor_id=acl.actor_id,`

```python
                    actor_id=acl.actor_id,
```

**Nhãn:** L390

**Mô tả:** Hành vi dòng 390.

**Vị trí file:** `pipeline.py` dòng 390 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 390; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.385 — Dòng 391: `role=acl.role,`

```python
                    role=acl.role,
```

**Nhãn:** L391

**Mô tả:** Hành vi dòng 391.

**Vị trí file:** `pipeline.py` dòng 391 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 391; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.386 — Dòng 392: `sql=sanitized,`

```python
                    sql=sanitized,
```

**Nhãn:** L392

**Mô tả:** Hành vi dòng 392.

**Vị trí file:** `pipeline.py` dòng 392 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 392; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.387 — Dòng 393: `target_db=tdb,`

```python
                    target_db=tdb,
```

**Nhãn:** L393

**Mô tả:** Hành vi dòng 393.

**Vị trí file:** `pipeline.py` dòng 393 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 393; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.388 — Dòng 394: `row_count=len(rows),`

```python
                    row_count=len(rows),
```

**Nhãn:** L394

**Mô tả:** Hành vi dòng 394.

**Vị trí file:** `pipeline.py` dòng 394 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 394; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.389 — Dòng 395: `outcome="ok",`

```python
                    outcome="ok",
```

**Nhãn:** L395

**Mô tả:** Hành vi dòng 395.

**Vị trí file:** `pipeline.py` dòng 395 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 395; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.390 — Dòng 396: `)`

```python
                )
```

**Nhãn:** L396

**Mô tả:** Hành vi dòng 396.

**Vị trí file:** `pipeline.py` dòng 396 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 396; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.391 — Dòng 397: `df = pd.DataFrame(rows)`

```python
                df = pd.DataFrame(rows)
```

**Nhãn:** DataFrame

**Mô tả:** pd.DataFrame rows.

**Vị trí file:** `pipeline.py` dòng 397 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 397; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.392 — Dòng 398: `path = raw_dir / f"query_{idx}.parquet"`

```python
                path = raw_dir / f"query_{idx}.parquet"
```

**Nhãn:** L398

**Mô tả:** Hành vi dòng 398.

**Vị trí file:** `pipeline.py` dòng 398 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 398; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.393 — Dòng 399: `df.to_parquet(path, index=False)`

```python
                df.to_parquet(path, index=False)
```

**Nhãn:** parquet

**Mô tả:** df.to_parquet raw_dir.

**Vị trí file:** `pipeline.py` dòng 399 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 399; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.394 — Dòng 400: `profile = build_result_profile(df)`

```python
                profile = build_result_profile(df)
```

**Nhãn:** L400

**Mô tả:** Hành vi dòng 400.

**Vị trí file:** `pipeline.py` dòng 400 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 400; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.395 — Dòng 401: `profiles.append(profile)`

```python
                profiles.append(profile)
```

**Nhãn:** L401

**Mô tả:** Hành vi dòng 401.

**Vị trí file:** `pipeline.py` dòng 401 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 401; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.396 — Dòng 402: `meta = query_meta[idx] if idx < len(query_meta) else {}`

```python
                meta = query_meta[idx] if idx < len(query_meta) else {}
```

**Nhãn:** L402

**Mô tả:** Hành vi dòng 402.

**Vị trí file:** `pipeline.py` dòng 402 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 402; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.397 — Dòng 403: `query_files.append(`

```python
                query_files.append(
```

**Nhãn:** L403

**Mô tả:** Hành vi dòng 403.

**Vị trí file:** `pipeline.py` dòng 403 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 403; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.398 — Dòng 404: `QueryResultFile(`

```python
                    QueryResultFile(
```

**Nhãn:** L404

**Mô tả:** Hành vi dòng 404.

**Vị trí file:** `pipeline.py` dòng 404 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 404; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.399 — Dòng 405: `query_index=idx,`

```python
                        query_index=idx,
```

**Nhãn:** L405

**Mô tả:** Hành vi dòng 405.

**Vị trí file:** `pipeline.py` dòng 405 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 405; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.400 — Dòng 406: `path=str(path),`

```python
                        path=str(path),
```

**Nhãn:** L406

**Mô tả:** Hành vi dòng 406.

**Vị trí file:** `pipeline.py` dòng 406 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 406; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.401 — Dòng 407: `row_count=len(df),`

```python
                        row_count=len(df),
```

**Nhãn:** L407

**Mô tả:** Hành vi dòng 407.

**Vị trí file:** `pipeline.py` dòng 407 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 407; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.402 — Dòng 408: `columns=list(df.columns.astype(str)),`

```python
                        columns=list(df.columns.astype(str)),
```

**Nhãn:** L408

**Mô tả:** Hành vi dòng 408.

**Vị trí file:** `pipeline.py` dòng 408 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 408; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.403 — Dòng 409: `)`

```python
                    )
```

**Nhãn:** L409

**Mô tả:** Hành vi dòng 409.

**Vị trí file:** `pipeline.py` dòng 409 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 409; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.404 — Dòng 410: `)`

```python
                )
```

**Nhãn:** L410

**Mô tả:** Hành vi dòng 410.

**Vị trí file:** `pipeline.py` dòng 410 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 410; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.405 — Dòng 411: `approved_sql.append(sanitized)`

```python
                approved_sql.append(sanitized)
```

**Nhãn:** L411

**Mô tả:** Hành vi dòng 411.

**Vị trí file:** `pipeline.py` dòng 411 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 411; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.406 — Dòng 412: `workflow.steps.append(`

```python
                workflow.steps.append(
```

**Nhãn:** L412

**Mô tả:** Hành vi dòng 412.

**Vị trí file:** `pipeline.py` dòng 412 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 412; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.407 — Dòng 413: `WorkflowStep(`

```python
                    WorkflowStep(
```

**Nhãn:** L413

**Mô tả:** Hành vi dòng 413.

**WorkflowStep:** step_id UUID mới; orchestrator persist workflow qua Redis sau run.

**Vị trí file:** `pipeline.py` dòng 413 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 413; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.408 — Dòng 414: `step_id=str(uuid4()),`

```python
                        step_id=str(uuid4()),
```

**Nhãn:** L414

**Mô tả:** Hành vi dòng 414.

**Vị trí file:** `pipeline.py` dòng 414 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 414; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.409 — Dòng 415: `trace_id=trace_id,`

```python
                        trace_id=trace_id,
```

**Nhãn:** L415

**Mô tả:** Hành vi dòng 415.

**Vị trí file:** `pipeline.py` dòng 415 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 415; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.410 — Dòng 416: `analysis_id=workflow.active_analysis_id or trace_id,`

```python
                        analysis_id=workflow.active_analysis_id or trace_id,
```

**Nhãn:** L416

**Mô tả:** Hành vi dòng 416.

**Vị trí file:** `pipeline.py` dòng 416 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 416; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.411 — Dòng 417: `step_type=WorkflowStepType.EXECUTE,`

```python
                        step_type=WorkflowStepType.EXECUTE,
```

**Nhãn:** L417

**Mô tả:** Hành vi dòng 417.

**Vị trí file:** `pipeline.py` dòng 417 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 417; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.412 — Dòng 418: `sql_attempt=sql_attempt,`

```python
                        sql_attempt=sql_attempt,
```

**Nhãn:** L418

**Mô tả:** Hành vi dòng 418.

**Vị trí file:** `pipeline.py` dòng 418 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 418; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.413 — Dòng 419: `query_index=idx,`

```python
                        query_index=idx,
```

**Nhãn:** L419

**Mô tả:** Hành vi dòng 419.

**Vị trí file:** `pipeline.py` dòng 419 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 419; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.414 — Dòng 420: `summary=f"rows={len(df)};role={meta.get('role', 'main')}",`

```python
                        summary=f"rows={len(df)};role={meta.get('role', 'main')}",
```

**Nhãn:** L420

**Mô tả:** Hành vi dòng 420.

**Vị trí file:** `pipeline.py` dòng 420 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 420; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.415 — Dòng 421: `)`

```python
                    )
```

**Nhãn:** L421

**Mô tả:** Hành vi dòng 421.

**Vị trí file:** `pipeline.py` dòng 421 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 421; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.416 — Dòng 422: `)`

```python
                )
```

**Nhãn:** L422

**Mô tả:** Hành vi dòng 422.

**Vị trí file:** `pipeline.py` dòng 422 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 422; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.417 — Dòng 423: ``

```python

```

**Nhãn:** L423

**Mô tả:** Hành vi dòng 423.

**Vị trí file:** `pipeline.py` dòng 423 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 423; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.418 — Dòng 424: `if not query_files:`

```python
            if not query_files:
```

**Nhãn:** no query_files

**Mô tả:** if not query_files — retry hoặc blocked.

**Vị trí file:** `pipeline.py` dòng 424 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 424; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.419 — Dòng 425: `if sql_attempt >= self.cfg.pipeline.max_sql_retries:`

```python
                if sql_attempt >= self.cfg.pipeline.max_sql_retries:
```

**Nhãn:** L425

**Mô tả:** Hành vi dòng 425.

**Vị trí file:** `pipeline.py` dòng 425 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 425; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.420 — Dòng 426: `return self._finish(`

```python
                    return self._finish(
```

**Nhãn:** L426

**Mô tả:** Hành vi dòng 426.

**_finish:** workflow IDLE, last_outcome, PipelineResult không needs_clarification.

**Vị trí file:** `pipeline.py` dòng 426 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 426; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.421 — Dòng 427: `trace_id,`

```python
                        trace_id,
```

**Nhãn:** L427

**Mô tả:** Hành vi dòng 427.

**Vị trí file:** `pipeline.py` dòng 427 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 427; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.422 — Dòng 428: `workflow,`

```python
                        workflow,
```

**Nhãn:** L428

**Mô tả:** Hành vi dòng 428.

**Vị trí file:** `pipeline.py` dòng 428 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 428; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.423 — Dòng 429: `AnalysisOutcome.POLICY_BLOCKED,`

```python
                        AnalysisOutcome.POLICY_BLOCKED,
```

**Nhãn:** L429

**Mô tả:** Hành vi dòng 429.

**Vị trí file:** `pipeline.py` dòng 429 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 429; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.424 — Dòng 430: `TechnicalSummary(outcome=AnalysisOutcome.POLICY_BLOCKED.valu...`

```python
                        TechnicalSummary(outcome=AnalysisOutcome.POLICY_BLOCKED.value),
```

**Nhãn:** L430

**Mô tả:** Hành vi dòng 430.

**Vị trí file:** `pipeline.py` dòng 430 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 430; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.425 — Dòng 431: `)`

```python
                    )
```

**Nhãn:** L431

**Mô tả:** Hành vi dòng 431.

**Vị trí file:** `pipeline.py` dòng 431 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 431; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.426 — Dòng 432: `continue`

```python
                continue
```

**Nhãn:** L432

**Mô tả:** Hành vi dòng 432.

**continue:** Bỏ phần còn lại vòng lặp hiện tại — sql_attempt hoặc query idx tiếp.

**Vị trí file:** `pipeline.py` dòng 432 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 432; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.427 — Dòng 433: ``

```python

```

**Nhãn:** L433

**Mô tả:** Hành vi dòng 433.

**Vị trí file:** `pipeline.py` dòng 433 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 433; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.428 — Dòng 434: `dataset = ExtractedDataset(trace_id=trace_id, queries=query_...`

```python
            dataset = ExtractedDataset(trace_id=trace_id, queries=query_files)
```

**Nhãn:** ExtractedDataset

**Mô tả:** trace_id + query_files.

**Vị trí file:** `pipeline.py` dòng 434 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 434; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.429 — Dòng 435: `merged_profile = self._merge_profiles(profiles)`

```python
            merged_profile = self._merge_profiles(profiles)
```

**Nhãn:** merge profiles

**Mô tả:** _merge_profiles profiles.

**Vị trí file:** `pipeline.py` dòng 435 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 435; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.430 — Dòng 436: `budget.record("IV")`

```python
            budget.record("IV")
```

**Nhãn:** L436

**Mô tả:** Hành vi dòng 436.

**Vị trí file:** `pipeline.py` dòng 436 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 436; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.431 — Dòng 437: `workflow.progress_step = WorkflowStepType.SANDBOX.value`

```python
            workflow.progress_step = WorkflowStepType.SANDBOX.value
```

**Nhãn:** L437

**Mô tả:** Hành vi dòng 437.

**Vị trí file:** `pipeline.py` dòng 437 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 437; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.432 — Dòng 438: `self._emit_progress(workflow, on_progress)`

```python
            self._emit_progress(workflow, on_progress)
```

**Nhãn:** L438

**Mô tả:** Hành vi dòng 438.

**Vị trí file:** `pipeline.py` dòng 438 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 438; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.433 — Dòng 439: ``

```python

```

**Nhãn:** L439

**Mô tả:** Hành vi dòng 439.

**Vị trí file:** `pipeline.py` dòng 439 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 439; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.434 — Dòng 440: `analysis_tools: list[dict[str, Any]] = promoted_tools`

```python
            analysis_tools: list[dict[str, Any]] = promoted_tools
```

**Nhãn:** L440

**Mô tả:** Hành vi dòng 440.

**Vị trí file:** `pipeline.py` dòng 440 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 440; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.435 — Dòng 441: `recipe_candidates: list[dict[str, Any]] = []`

```python
            recipe_candidates: list[dict[str, Any]] = []
```

**Nhãn:** L441

**Mô tả:** Hành vi dòng 441.

**Vị trí file:** `pipeline.py` dòng 441 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 441; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.436 — Dòng 442: `candidates_by_subtask: dict[str, list] = {}`

```python
            candidates_by_subtask: dict[str, list] = {}
```

**Nhãn:** L442

**Mô tả:** Hành vi dòng 442.

**Vị trí file:** `pipeline.py` dòng 442 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 442; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.437 — Dòng 443: ``

```python

```

**Nhãn:** L443

**Mô tả:** Hành vi dòng 443.

**Vị trí file:** `pipeline.py` dòng 443 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 443; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.438 — Dòng 444: `def _function_allowed(tool_id: str) -> bool:`

```python
            def _function_allowed(tool_id: str) -> bool:
```

**Nhãn:** _function_allowed

**Mô tả:** Nested function gate sandbox tools.

**Vị trí file:** `pipeline.py` dòng 444 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 444; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.439 — Dòng 445: `# Recipes without a tool_id are inline steps (not a promoted`

```python
                # Recipes without a tool_id are inline steps (not a promoted
```

**Nhãn:** L445

**Mô tả:** Hành vi dòng 445.

**Vị trí file:** `pipeline.py` dòng 445 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 445; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.440 — Dòng 446: `# function) and are gated by the sandbox tool grant instead.`

```python
                # function) and are gated by the sandbox tool grant instead.
```

**Nhãn:** L446

**Mô tả:** Hành vi dòng 446.

**Vị trí file:** `pipeline.py` dòng 446 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 446; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.441 — Dòng 447: `return not tool_id or self.context_policy.can_invoke_functio...`

```python
                return not tool_id or self.context_policy.can_invoke_function(permissions, tool_id)
```

**Nhãn:** L447

**Mô tả:** Hành vi dòng 447.

**ContextPolicy:** Gate quyền tool/function/SQL — POLICY_BLOCKED nếu thiếu grant.

**Vị trí file:** `pipeline.py` dòng 447 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 447; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.442 — Dòng 448: ``

```python

```

**Nhãn:** L448

**Mô tả:** Hành vi dòng 448.

**Vị trí file:** `pipeline.py` dòng 448 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 448; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.443 — Dòng 449: `if brief.plan:`

```python
            if brief.plan:
```

**Nhãn:** L449

**Mô tả:** Hành vi dòng 449.

**Vị trí file:** `pipeline.py` dòng 449 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 449; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.444 — Dòng 450: `for subtask in brief.plan.subtasks:`

```python
                for subtask in brief.plan.subtasks:
```

**Nhãn:** L450

**Mô tả:** Hành vi dòng 450.

**Vị trí file:** `pipeline.py` dòng 450 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 450; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.445 — Dòng 451: `if self.analysis_tool_registry:`

```python
                    if self.analysis_tool_registry:
```

**Nhãn:** L451

**Mô tả:** Hành vi dòng 451.

**Vị trí file:** `pipeline.py` dòng 451 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 451; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.446 — Dòng 452: `ranked = self.analysis_tool_registry.find_candidates(subtask...`

```python
                        ranked = self.analysis_tool_registry.find_candidates(subtask.intent, top_k=5)
```

**Nhãn:** L452

**Mô tả:** Hành vi dòng 452.

**Vị trí file:** `pipeline.py` dòng 452 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 452; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.447 — Dòng 453: `else:`

```python
                    else:
```

**Nhãn:** L453

**Mô tả:** Hành vi dòng 453.

**Vị trí file:** `pipeline.py` dòng 453 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 453; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.448 — Dòng 454: `ranked = rank_candidates(subtask.intent, promoted_tools, top...`

```python
                        ranked = rank_candidates(subtask.intent, promoted_tools, top_k=5)
```

**Nhãn:** L454

**Mô tả:** Hành vi dòng 454.

**Vị trí file:** `pipeline.py` dòng 454 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 454; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.449 — Dòng 455: `ranked = [c for c in ranked if _function_allowed(getattr(c, ...`

```python
                    ranked = [c for c in ranked if _function_allowed(getattr(c, "tool_id", ""))]
```

**Nhãn:** L455

**Mô tả:** Hành vi dòng 455.

**Vị trí file:** `pipeline.py` dòng 455 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 455; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.450 — Dòng 456: `candidates_by_subtask[subtask.id] = ranked`

```python
                    candidates_by_subtask[subtask.id] = ranked
```

**Nhãn:** L456

**Mô tả:** Hành vi dòng 456.

**Vị trí file:** `pipeline.py` dòng 456 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 456; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.451 — Dòng 457: `for c in ranked:`

```python
                    for c in ranked:
```

**Nhãn:** L457

**Mô tả:** Hành vi dòng 457.

**Vị trí file:** `pipeline.py` dòng 457 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 457; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.452 — Dòng 458: `recipe_candidates.append({**c.model_dump(), "subtask_id": su...`

```python
                        recipe_candidates.append({**c.model_dump(), "subtask_id": subtask.id})
```

**Nhãn:** L458

**Mô tả:** Hành vi dòng 458.

**model_dump:** JSON-serializable cho HTTP agent; permissions dùng mode="json".

**Vị trí file:** `pipeline.py` dòng 458 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 458; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.453 — Dòng 459: ``

```python

```

**Nhãn:** L459

**Mô tả:** Hành vi dòng 459.

**Vị trí file:** `pipeline.py` dòng 459 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 459; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.454 — Dòng 460: `paths_for_plan = [q.path for q in query_files]`

```python
            paths_for_plan = [q.path for q in query_files]
```

**Nhãn:** L460

**Mô tả:** Hành vi dòng 460.

**Vị trí file:** `pipeline.py` dòng 460 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 460; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.455 — Dòng 461: `execution_steps, _coverage_preview = build_execution_plan(`

```python
            execution_steps, _coverage_preview = build_execution_plan(
```

**Nhãn:** build_execution_plan

**Mô tả:** execution_steps cho IV.

**Vị trí file:** `pipeline.py` dòng 461 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 461; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.456 — Dòng 462: `brief.plan,`

```python
                brief.plan,
```

**Nhãn:** L462

**Mô tả:** Hành vi dòng 462.

**Vị trí file:** `pipeline.py` dòng 462 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 462; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.457 — Dòng 463: `dataset_paths=paths_for_plan,`

```python
                dataset_paths=paths_for_plan,
```

**Nhãn:** L463

**Mô tả:** Hành vi dòng 463.

**Vị trí file:** `pipeline.py` dòng 463 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 463; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.458 — Dòng 464: `query_meta=query_meta,`

```python
                query_meta=query_meta,
```

**Nhãn:** L464

**Mô tả:** Hành vi dòng 464.

**Vị trí file:** `pipeline.py` dòng 464 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 464; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.459 — Dòng 465: `candidates_by_subtask=candidates_by_subtask,`

```python
                candidates_by_subtask=candidates_by_subtask,
```

**Nhãn:** L465

**Mô tả:** Hành vi dòng 465.

**Vị trí file:** `pipeline.py` dòng 465 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 465; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.460 — Dòng 466: `brief=brief,`

```python
                brief=brief,
```

**Nhãn:** L466

**Mô tả:** Hành vi dòng 466.

**Vị trí file:** `pipeline.py` dòng 466 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 466; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.461 — Dòng 467: `)`

```python
            )
```

**Nhãn:** L467

**Mô tả:** Hành vi dòng 467.

**Vị trí file:** `pipeline.py` dòng 467 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 467; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.462 — Dòng 468: ``

```python

```

**Nhãn:** L468

**Mô tả:** Hành vi dòng 468.

**Vị trí file:** `pipeline.py` dòng 468 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 468; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.463 — Dòng 469: `iv_raw = self.agent_invoker.invoke(`

```python
            iv_raw = self.agent_invoker.invoke(
```

**Nhãn:** invoke IV

**Mô tả:** agent IV analyze mode.

**Invoke agent:** Payload dict; metadata mode plan_sql/review/analyze. Lỗi HTTP propagate — pipeline không catch network.

**Vị trí file:** `pipeline.py` dòng 469 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 469; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.464 — Dòng 470: `"IV",`

```python
                "IV",
```

**Nhãn:** L470

**Mô tả:** Hành vi dòng 470.

**Vị trí file:** `pipeline.py` dòng 470 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 470; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.465 — Dòng 471: `{`

```python
                {
```

**Nhãn:** L471

**Mô tả:** Hành vi dòng 471.

**Vị trí file:** `pipeline.py` dòng 471 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 471; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.466 — Dòng 472: `"brief": brief.model_dump(),`

```python
                    "brief": brief.model_dump(),
```

**Nhãn:** L472

**Mô tả:** Hành vi dòng 472.

**model_dump:** JSON-serializable cho HTTP agent; permissions dùng mode="json".

**Vị trí file:** `pipeline.py` dòng 472 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 472; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.467 — Dòng 473: `"dataset_manifest": dataset.model_dump(),`

```python
                    "dataset_manifest": dataset.model_dump(),
```

**Nhãn:** L473

**Mô tả:** Hành vi dòng 473.

**model_dump:** JSON-serializable cho HTTP agent; permissions dùng mode="json".

**Vị trí file:** `pipeline.py` dòng 473 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 473; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.468 — Dòng 474: `"result_profile": merged_profile.model_dump(),`

```python
                    "result_profile": merged_profile.model_dump(),
```

**Nhãn:** L474

**Mô tả:** Hành vi dòng 474.

**model_dump:** JSON-serializable cho HTTP agent; permissions dùng mode="json".

**Vị trí file:** `pipeline.py` dòng 474 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 474; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.469 — Dòng 475: `"query_meta": query_meta,`

```python
                    "query_meta": query_meta,
```

**Nhãn:** L475

**Mô tả:** Hành vi dòng 475.

**Vị trí file:** `pipeline.py` dòng 475 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 475; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.470 — Dòng 476: `"out_dir": str(out_dir),`

```python
                    "out_dir": str(out_dir),
```

**Nhãn:** L476

**Mô tả:** Hành vi dòng 476.

**Vị trí file:** `pipeline.py` dòng 476 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 476; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.471 — Dòng 477: `"max_steps": self.cfg.pipeline.iv_max_steps,`

```python
                    "max_steps": self.cfg.pipeline.iv_max_steps,
```

**Nhãn:** L477

**Mô tả:** Hành vi dòng 477.

**Vị trí file:** `pipeline.py` dòng 477 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 477; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.472 — Dòng 478: `"analysis_tools": analysis_tools,`

```python
                    "analysis_tools": analysis_tools,
```

**Nhãn:** L478

**Mô tả:** Hành vi dòng 478.

**Vị trí file:** `pipeline.py` dòng 478 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 478; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.473 — Dòng 479: `"recipe_candidates": recipe_candidates,`

```python
                    "recipe_candidates": recipe_candidates,
```

**Nhãn:** L479

**Mô tả:** Hành vi dòng 479.

**Vị trí file:** `pipeline.py` dòng 479 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 479; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.474 — Dòng 480: `"analysis_plan": brief.plan.model_dump() if brief.plan else ...`

```python
                    "analysis_plan": brief.plan.model_dump() if brief.plan else None,
```

**Nhãn:** L480

**Mô tả:** Hành vi dòng 480.

**model_dump:** JSON-serializable cho HTTP agent; permissions dùng mode="json".

**Vị trí file:** `pipeline.py` dòng 480 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 480; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.475 — Dòng 481: `"execution_plan": [s.model_dump() for s in execution_steps],`

```python
                    "execution_plan": [s.model_dump() for s in execution_steps],
```

**Nhãn:** L481

**Mô tả:** Hành vi dòng 481.

**model_dump:** JSON-serializable cho HTTP agent; permissions dùng mode="json".

**Vị trí file:** `pipeline.py` dòng 481 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 481; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.476 — Dòng 482: `"domain_rules_excerpt": domain_excerpt,`

```python
                    "domain_rules_excerpt": domain_excerpt,
```

**Nhãn:** L482

**Mô tả:** Hành vi dòng 482.

**Vị trí file:** `pipeline.py` dòng 482 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 482; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.477 — Dòng 483: `"permissions": permissions.model_dump(mode="json"),`

```python
                    "permissions": permissions.model_dump(mode="json"),
```

**Nhãn:** L483

**Mô tả:** Hành vi dòng 483.

**model_dump:** JSON-serializable cho HTTP agent; permissions dùng mode="json".

**Vị trí file:** `pipeline.py` dòng 483 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 483; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.478 — Dòng 484: `},`

```python
                },
```

**Nhãn:** L484

**Mô tả:** Hành vi dòng 484.

**Vị trí file:** `pipeline.py` dòng 484 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 484; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.479 — Dòng 485: `{"mode": "analyze"},`

```python
                {"mode": "analyze"},
```

**Nhãn:** L485

**Mô tả:** Hành vi dòng 485.

**Vị trí file:** `pipeline.py` dòng 485 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 485; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.480 — Dòng 486: `)`

```python
            )
```

**Nhãn:** L486

**Mô tả:** Hành vi dòng 486.

**Vị trí file:** `pipeline.py` dòng 486 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 486; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.481 — Dòng 487: `try:`

```python
            try:
```

**Nhãn:** L487

**Mô tả:** Hành vi dòng 487.

**Vị trí file:** `pipeline.py` dòng 487 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 487; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.482 — Dòng 488: `iv_parsed = parse_agent_response("IV", iv_raw)`

```python
                iv_parsed = parse_agent_response("IV", iv_raw)
```

**Nhãn:** L488

**Mô tả:** Hành vi dòng 488.

**Vị trí file:** `pipeline.py` dòng 488 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 488; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.483 — Dòng 489: `except ContractInvalidError as exc:`

```python
            except ContractInvalidError as exc:
```

**Nhãn:** L489

**Mô tả:** Hành vi dòng 489.

**Vị trí file:** `pipeline.py` dòng 489 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 489; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.484 — Dòng 490: `return self._finish(`

```python
                return self._finish(
```

**Nhãn:** L490

**Mô tả:** Hành vi dòng 490.

**_finish:** workflow IDLE, last_outcome, PipelineResult không needs_clarification.

**Vị trí file:** `pipeline.py` dòng 490 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 490; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.485 — Dòng 491: `trace_id,`

```python
                    trace_id,
```

**Nhãn:** L491

**Mô tả:** Hành vi dòng 491.

**Vị trí file:** `pipeline.py` dòng 491 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 491; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.486 — Dòng 492: `workflow,`

```python
                    workflow,
```

**Nhãn:** L492

**Mô tả:** Hành vi dòng 492.

**Vị trí file:** `pipeline.py` dòng 492 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 492; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.487 — Dòng 493: `AnalysisOutcome.ERROR,`

```python
                    AnalysisOutcome.ERROR,
```

**Nhãn:** L493

**Mô tả:** Hành vi dòng 493.

**Vị trí file:** `pipeline.py` dòng 493 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 493; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.488 — Dòng 494: `TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveat...`

```python
                    TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveats=[str(exc)]),
```

**Nhãn:** L494

**Mô tả:** Hành vi dòng 494.

**Vị trí file:** `pipeline.py` dòng 494 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 494; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.489 — Dòng 495: `)`

```python
                )
```

**Nhãn:** L495

**Mô tả:** Hành vi dòng 495.

**Vị trí file:** `pipeline.py` dòng 495 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 495; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.490 — Dòng 496: `if not isinstance(iv_parsed, AnalystResponse):`

```python
            if not isinstance(iv_parsed, AnalystResponse):
```

**Nhãn:** L496

**Mô tả:** Hành vi dòng 496.

**Vị trí file:** `pipeline.py` dòng 496 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 496; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.491 — Dòng 497: `return self._finish(`

```python
                return self._finish(
```

**Nhãn:** L497

**Mô tả:** Hành vi dòng 497.

**_finish:** workflow IDLE, last_outcome, PipelineResult không needs_clarification.

**Vị trí file:** `pipeline.py` dòng 497 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 497; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.492 — Dòng 498: `trace_id,`

```python
                    trace_id,
```

**Nhãn:** L498

**Mô tả:** Hành vi dòng 498.

**Vị trí file:** `pipeline.py` dòng 498 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 498; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.493 — Dòng 499: `workflow,`

```python
                    workflow,
```

**Nhãn:** L499

**Mô tả:** Hành vi dòng 499.

**Vị trí file:** `pipeline.py` dòng 499 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 499; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.494 — Dòng 500: `AnalysisOutcome.ERROR,`

```python
                    AnalysisOutcome.ERROR,
```

**Nhãn:** L500

**Mô tả:** Hành vi dòng 500.

**Vị trí file:** `pipeline.py` dòng 500 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 500; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.495 — Dòng 501: `TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveat...`

```python
                    TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveats=["invalid_agent_iv"]),
```

**Nhãn:** L501

**Mô tả:** Hành vi dòng 501.

**Vị trí file:** `pipeline.py` dòng 501 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 501; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.496 — Dòng 502: `)`

```python
                )
```

**Nhãn:** L502

**Mô tả:** Hành vi dòng 502.

**Vị trí file:** `pipeline.py` dòng 502 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 502; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.497 — Dòng 503: `iv_action = iv_parsed.action`

```python
            iv_action = iv_parsed.action
```

**Nhãn:** iv_action

**Mô tả:** iv_parsed.action — nhánh IV.

**Vị trí file:** `pipeline.py` dòng 503 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 503; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.498 — Dòng 504: ``

```python

```

**Nhãn:** L504

**Mô tả:** Hành vi dòng 504.

**Vị trí file:** `pipeline.py` dòng 504 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 504; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.499 — Dòng 505: `if iv_action == "data_feedback":`

```python
            if iv_action == "data_feedback":
```

**Nhãn:** data_feedback

**Mô tả:** iv_action data_feedback.

**Vị trí file:** `pipeline.py` dòng 505 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 505; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.500 — Dòng 506: `feedback_raw = iv_parsed.data_feedback or {}`

```python
                feedback_raw = iv_parsed.data_feedback or {}
```

**Nhãn:** L506

**Mô tả:** Hành vi dòng 506.

**Vị trí file:** `pipeline.py` dòng 506 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 506; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.501 — Dòng 507: `inbox["data_feedback"] = feedback_raw`

```python
                inbox["data_feedback"] = feedback_raw
```

**Nhãn:** L507

**Mô tả:** Hành vi dòng 507.

**Inbox:** Agent sau trong cùng run đọc qua payload — II nhận full inbox 156.

**Vị trí file:** `pipeline.py` dòng 507 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 507; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.502 — Dòng 508: `try:`

```python
                try:
```

**Nhãn:** L508

**Mô tả:** Hành vi dòng 508.

**Vị trí file:** `pipeline.py` dòng 508 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 508; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.503 — Dòng 509: `fb = DataFeedback.model_validate(feedback_raw)`

```python
                    fb = DataFeedback.model_validate(feedback_raw)
```

**Nhãn:** L509

**Mô tả:** Hành vi dòng 509.

**Vị trí file:** `pipeline.py` dòng 509 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 509; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.504 — Dòng 510: `except Exception:  # noqa: BLE001`

```python
                except Exception:  # noqa: BLE001
```

**Nhãn:** L510

**Mô tả:** Hành vi dòng 510.

**Vị trí file:** `pipeline.py` dòng 510 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 510; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.505 — Dòng 511: `fb = DataFeedback(`

```python
                    fb = DataFeedback(
```

**Nhãn:** L511

**Mô tả:** Hành vi dòng 511.

**Vị trí file:** `pipeline.py` dòng 511 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 511; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.506 — Dòng 512: `needs_sql_retry=True,`

```python
                        needs_sql_retry=True,
```

**Nhãn:** L512

**Mô tả:** Hành vi dòng 512.

**Vị trí file:** `pipeline.py` dòng 512 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 512; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.507 — Dòng 513: `issue="invalid_feedback",`

```python
                        issue="invalid_feedback",
```

**Nhãn:** L513

**Mô tả:** Hành vi dòng 513.

**Vị trí file:** `pipeline.py` dòng 513 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 513; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.508 — Dòng 514: `summary="IV feedback invalid",`

```python
                        summary="IV feedback invalid",
```

**Nhãn:** L514

**Mô tả:** Hành vi dòng 514.

**Vị trí file:** `pipeline.py` dòng 514 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 514; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.509 — Dòng 515: `suggested_intent_fix=brief.intent,`

```python
                        suggested_intent_fix=brief.intent,
```

**Nhãn:** L515

**Mô tả:** Hành vi dòng 515.

**Vị trí file:** `pipeline.py` dòng 515 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 515; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.510 — Dòng 516: `)`

```python
                    )
```

**Nhãn:** L516

**Mô tả:** Hành vi dòng 516.

**Vị trí file:** `pipeline.py` dòng 516 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 516; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.511 — Dòng 517: `inbox["data_feedback"] = fb.model_dump()`

```python
                    inbox["data_feedback"] = fb.model_dump()
```

**Nhãn:** L517

**Mô tả:** Hành vi dòng 517.

**Inbox:** Agent sau trong cùng run đọc qua payload — II nhận full inbox 156.

**model_dump:** JSON-serializable cho HTTP agent; permissions dùng mode="json".

**Vị trí file:** `pipeline.py` dòng 517 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 517; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.512 — Dòng 518: `workflow.steps.append(`

```python
                workflow.steps.append(
```

**Nhãn:** L518

**Mô tả:** Hành vi dòng 518.

**Vị trí file:** `pipeline.py` dòng 518 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 518; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.513 — Dòng 519: `WorkflowStep(`

```python
                    WorkflowStep(
```

**Nhãn:** L519

**Mô tả:** Hành vi dòng 519.

**WorkflowStep:** step_id UUID mới; orchestrator persist workflow qua Redis sau run.

**Vị trí file:** `pipeline.py` dòng 519 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 519; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.514 — Dòng 520: `step_id=str(uuid4()),`

```python
                        step_id=str(uuid4()),
```

**Nhãn:** L520

**Mô tả:** Hành vi dòng 520.

**Vị trí file:** `pipeline.py` dòng 520 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 520; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.515 — Dòng 521: `trace_id=trace_id,`

```python
                        trace_id=trace_id,
```

**Nhãn:** L521

**Mô tả:** Hành vi dòng 521.

**Vị trí file:** `pipeline.py` dòng 521 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 521; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.516 — Dòng 522: `analysis_id=workflow.active_analysis_id or trace_id,`

```python
                        analysis_id=workflow.active_analysis_id or trace_id,
```

**Nhãn:** L522

**Mô tả:** Hành vi dòng 522.

**Vị trí file:** `pipeline.py` dòng 522 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 522; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.517 — Dòng 523: `step_type=WorkflowStepType.DATA_FEEDBACK,`

```python
                        step_type=WorkflowStepType.DATA_FEEDBACK,
```

**Nhãn:** L523

**Mô tả:** Hành vi dòng 523.

**Vị trí file:** `pipeline.py` dòng 523 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 523; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.518 — Dòng 524: `sql_attempt=sql_attempt,`

```python
                        sql_attempt=sql_attempt,
```

**Nhãn:** L524

**Mô tả:** Hành vi dòng 524.

**Vị trí file:** `pipeline.py` dòng 524 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 524; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.519 — Dòng 525: `summary=fb.issue,`

```python
                        summary=fb.issue,
```

**Nhãn:** L525

**Mô tả:** Hành vi dòng 525.

**Vị trí file:** `pipeline.py` dòng 525 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 525; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.520 — Dòng 526: `)`

```python
                    )
```

**Nhãn:** L526

**Mô tả:** Hành vi dòng 526.

**Vị trí file:** `pipeline.py` dòng 526 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 526; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.521 — Dòng 527: `)`

```python
                )
```

**Nhãn:** L527

**Mô tả:** Hành vi dòng 527.

**Vị trí file:** `pipeline.py` dòng 527 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 527; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.522 — Dòng 528: `if fb.diagnosis == "impossible":`

```python
                if fb.diagnosis == "impossible":
```

**Nhãn:** L528

**Mô tả:** Hành vi dòng 528.

**Vị trí file:** `pipeline.py` dòng 528 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 528; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.523 — Dòng 529: `return self._finish(`

```python
                    return self._finish(
```

**Nhãn:** L529

**Mô tả:** Hành vi dòng 529.

**_finish:** workflow IDLE, last_outcome, PipelineResult không needs_clarification.

**Vị trí file:** `pipeline.py` dòng 529 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 529; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.524 — Dòng 530: `trace_id,`

```python
                        trace_id,
```

**Nhãn:** L530

**Mô tả:** Hành vi dòng 530.

**Vị trí file:** `pipeline.py` dòng 530 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 530; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.525 — Dòng 531: `workflow,`

```python
                        workflow,
```

**Nhãn:** L531

**Mô tả:** Hành vi dòng 531.

**Vị trí file:** `pipeline.py` dòng 531 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 531; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.526 — Dòng 532: `AnalysisOutcome.IMPOSSIBLE,`

```python
                        AnalysisOutcome.IMPOSSIBLE,
```

**Nhãn:** L532

**Mô tả:** Hành vi dòng 532.

**Vị trí file:** `pipeline.py` dòng 532 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 532; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.527 — Dòng 533: `TechnicalSummary(`

```python
                        TechnicalSummary(
```

**Nhãn:** L533

**Mô tả:** Hành vi dòng 533.

**Vị trí file:** `pipeline.py` dòng 533 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 533; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.528 — Dòng 534: `outcome=AnalysisOutcome.IMPOSSIBLE.value,`

```python
                            outcome=AnalysisOutcome.IMPOSSIBLE.value,
```

**Nhãn:** L534

**Mô tả:** Hành vi dòng 534.

**Vị trí file:** `pipeline.py` dòng 534 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 534; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.529 — Dòng 535: `caveats=[fb.summary],`

```python
                            caveats=[fb.summary],
```

**Nhãn:** L535

**Mô tả:** Hành vi dòng 535.

**Vị trí file:** `pipeline.py` dòng 535 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 535; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.530 — Dòng 536: `empty_reason=fb.issue,`

```python
                            empty_reason=fb.issue,
```

**Nhãn:** L536

**Mô tả:** Hành vi dòng 536.

**Vị trí file:** `pipeline.py` dòng 536 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 536; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.531 — Dòng 537: `),`

```python
                        ),
```

**Nhãn:** L537

**Mô tả:** Hành vi dòng 537.

**Vị trí file:** `pipeline.py` dòng 537 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 537; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.532 — Dòng 538: `)`

```python
                    )
```

**Nhãn:** L538

**Mô tả:** Hành vi dòng 538.

**Vị trí file:** `pipeline.py` dòng 538 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 538; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.533 — Dòng 539: `if iv_parsed.suggest_clarify:`

```python
                if iv_parsed.suggest_clarify:
```

**Nhãn:** L539

**Mô tả:** Hành vi dòng 539.

**Vị trí file:** `pipeline.py` dòng 539 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 539; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.534 — Dòng 540: `needs_clarification = ClarificationRequest.model_validate(iv...`

```python
                    needs_clarification = ClarificationRequest.model_validate(iv_parsed.suggest_clarify)
```

**Nhãn:** L540

**Mô tả:** Hành vi dòng 540.

**Vị trí file:** `pipeline.py` dòng 540 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 540; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.535 — Dòng 541: `workflow.status = WorkflowStatus.AWAITING_CLARIFICATION`

```python
                    workflow.status = WorkflowStatus.AWAITING_CLARIFICATION
```

**Nhãn:** L541

**Mô tả:** Hành vi dòng 541.

**Vị trí file:** `pipeline.py` dòng 541 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 541; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.536 — Dòng 542: `return PipelineResult(`

```python
                    return PipelineResult(
```

**Nhãn:** L542

**Mô tả:** Hành vi dòng 542.

**Vị trí file:** `pipeline.py` dòng 542 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 542; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.537 — Dòng 543: `trace_id=trace_id,`

```python
                        trace_id=trace_id,
```

**Nhãn:** L543

**Mô tả:** Hành vi dòng 543.

**Vị trí file:** `pipeline.py` dòng 543 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 543; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.538 — Dòng 544: `analysis_id=workflow.active_analysis_id or trace_id,`

```python
                        analysis_id=workflow.active_analysis_id or trace_id,
```

**Nhãn:** L544

**Mô tả:** Hành vi dòng 544.

**Vị trí file:** `pipeline.py` dòng 544 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 544; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.539 — Dòng 545: `outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value,`

```python
                        outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value,
```

**Nhãn:** L545

**Mô tả:** Hành vi dòng 545.

**Vị trí file:** `pipeline.py` dòng 545 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 545; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.540 — Dòng 546: `technical_summary=TechnicalSummary(outcome=AnalysisOutcome.N...`

```python
                        technical_summary=TechnicalSummary(outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value),
```

**Nhãn:** L546

**Mô tả:** Hành vi dòng 546.

**Vị trí file:** `pipeline.py` dòng 546 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 546; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.541 — Dòng 547: `workflow_steps=workflow.steps,`

```python
                        workflow_steps=workflow.steps,
```

**Nhãn:** L547

**Mô tả:** Hành vi dòng 547.

**Vị trí file:** `pipeline.py` dòng 547 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 547; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.542 — Dòng 548: `needs_clarification=needs_clarification,`

```python
                        needs_clarification=needs_clarification,
```

**Nhãn:** L548

**Mô tả:** Hành vi dòng 548.

**Vị trí file:** `pipeline.py` dòng 548 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 548; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.543 — Dòng 549: `)`

```python
                    )
```

**Nhãn:** L549

**Mô tả:** Hành vi dòng 549.

**Vị trí file:** `pipeline.py` dòng 549 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 549; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.544 — Dòng 550: `if fb.diagnosis == "needs_probe" and fb.probe_requests:`

```python
                if fb.diagnosis == "needs_probe" and fb.probe_requests:
```

**Nhãn:** L550

**Mô tả:** Hành vi dòng 550.

**Vị trí file:** `pipeline.py` dòng 550 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 550; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.545 — Dòng 551: `inbox["probe_mode"] = True`

```python
                    inbox["probe_mode"] = True
```

**Nhãn:** L551

**Mô tả:** Hành vi dòng 551.

**Inbox:** Agent sau trong cùng run đọc qua payload — II nhận full inbox 156.

**Vị trí file:** `pipeline.py` dòng 551 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 551; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.546 — Dòng 552: `if self.domain_rule_store and fb.confirmed_rules:`

```python
                if self.domain_rule_store and fb.confirmed_rules:
```

**Nhãn:** L552

**Mô tả:** Hành vi dòng 552.

**Vị trí file:** `pipeline.py` dòng 552 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 552; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.547 — Dòng 553: `for rule in fb.confirmed_rules:`

```python
                    for rule in fb.confirmed_rules:
```

**Nhãn:** L553

**Mô tả:** Hành vi dòng 553.

**Vị trí file:** `pipeline.py` dòng 553 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 553; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.548 — Dòng 554: `self.domain_rule_store.stage_candidate(rule, trace_id=trace_...`

```python
                        self.domain_rule_store.stage_candidate(rule, trace_id=trace_id)
```

**Nhãn:** L554

**Mô tả:** Hành vi dòng 554.

**Vị trí file:** `pipeline.py` dòng 554 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 554; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.549 — Dòng 555: `continue`

```python
                continue
```

**Nhãn:** continue sql

**Mô tả:** continue sau data_feedback — sql_attempt++.

**continue:** Bỏ phần còn lại vòng lặp hiện tại — sql_attempt hoặc query idx tiếp.

**Vị trí file:** `pipeline.py` dòng 555 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 555; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.550 — Dòng 556: ``

```python

```

**Nhãn:** L556

**Mô tả:** Hành vi dòng 556.

**Vị trí file:** `pipeline.py` dòng 556 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 556; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.551 — Dòng 557: `if iv_action == "suggest_clarify":`

```python
            if iv_action == "suggest_clarify":
```

**Nhãn:** L557

**Mô tả:** Hành vi dòng 557.

**Vị trí file:** `pipeline.py` dòng 557 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 557; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.552 — Dòng 558: `needs_clarification = ClarificationRequest.model_validate(iv...`

```python
                needs_clarification = ClarificationRequest.model_validate(iv_parsed.clarification_request)
```

**Nhãn:** L558

**Mô tả:** Hành vi dòng 558.

**Vị trí file:** `pipeline.py` dòng 558 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 558; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.553 — Dòng 559: `workflow.status = WorkflowStatus.AWAITING_CLARIFICATION`

```python
                workflow.status = WorkflowStatus.AWAITING_CLARIFICATION
```

**Nhãn:** L559

**Mô tả:** Hành vi dòng 559.

**Vị trí file:** `pipeline.py` dòng 559 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 559; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.554 — Dòng 560: `return PipelineResult(`

```python
                return PipelineResult(
```

**Nhãn:** L560

**Mô tả:** Hành vi dòng 560.

**Vị trí file:** `pipeline.py` dòng 560 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 560; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.555 — Dòng 561: `trace_id=trace_id,`

```python
                    trace_id=trace_id,
```

**Nhãn:** L561

**Mô tả:** Hành vi dòng 561.

**Vị trí file:** `pipeline.py` dòng 561 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 561; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.556 — Dòng 562: `analysis_id=workflow.active_analysis_id or trace_id,`

```python
                    analysis_id=workflow.active_analysis_id or trace_id,
```

**Nhãn:** L562

**Mô tả:** Hành vi dòng 562.

**Vị trí file:** `pipeline.py` dòng 562 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 562; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.557 — Dòng 563: `outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value,`

```python
                    outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value,
```

**Nhãn:** L563

**Mô tả:** Hành vi dòng 563.

**Vị trí file:** `pipeline.py` dòng 563 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 563; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.558 — Dòng 564: `technical_summary=TechnicalSummary(outcome=AnalysisOutcome.N...`

```python
                    technical_summary=TechnicalSummary(outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value),
```

**Nhãn:** L564

**Mô tả:** Hành vi dòng 564.

**Vị trí file:** `pipeline.py` dòng 564 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 564; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.559 — Dòng 565: `workflow_steps=workflow.steps,`

```python
                    workflow_steps=workflow.steps,
```

**Nhãn:** L565

**Mô tả:** Hành vi dòng 565.

**Vị trí file:** `pipeline.py` dòng 565 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 565; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.560 — Dòng 566: `needs_clarification=needs_clarification,`

```python
                    needs_clarification=needs_clarification,
```

**Nhãn:** L566

**Mô tả:** Hành vi dòng 566.

**Vị trí file:** `pipeline.py` dòng 566 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 566; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.561 — Dòng 567: `)`

```python
                )
```

**Nhãn:** L567

**Mô tả:** Hành vi dòng 567.

**Vị trí file:** `pipeline.py` dòng 567 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 567; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.562 — Dòng 568: ``

```python

```

**Nhãn:** L568

**Mô tả:** Hành vi dòng 568.

**Vị trí file:** `pipeline.py` dòng 568 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 568; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.563 — Dòng 569: `if iv_action == "impossible":`

```python
            if iv_action == "impossible":
```

**Nhãn:** L569

**Mô tả:** Hành vi dòng 569.

**Vị trí file:** `pipeline.py` dòng 569 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 569; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.564 — Dòng 570: `return self._finish(`

```python
                return self._finish(
```

**Nhãn:** L570

**Mô tả:** Hành vi dòng 570.

**_finish:** workflow IDLE, last_outcome, PipelineResult không needs_clarification.

**Vị trí file:** `pipeline.py` dòng 570 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 570; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.565 — Dòng 571: `trace_id,`

```python
                    trace_id,
```

**Nhãn:** L571

**Mô tả:** Hành vi dòng 571.

**Vị trí file:** `pipeline.py` dòng 571 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 571; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.566 — Dòng 572: `workflow,`

```python
                    workflow,
```

**Nhãn:** L572

**Mô tả:** Hành vi dòng 572.

**Vị trí file:** `pipeline.py` dòng 572 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 572; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.567 — Dòng 573: `AnalysisOutcome.IMPOSSIBLE,`

```python
                    AnalysisOutcome.IMPOSSIBLE,
```

**Nhãn:** L573

**Mô tả:** Hành vi dòng 573.

**Vị trí file:** `pipeline.py` dòng 573 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 573; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.568 — Dòng 574: `TechnicalSummary(`

```python
                    TechnicalSummary(
```

**Nhãn:** L574

**Mô tả:** Hành vi dòng 574.

**Vị trí file:** `pipeline.py` dòng 574 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 574; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.569 — Dòng 575: `outcome=AnalysisOutcome.IMPOSSIBLE.value,`

```python
                        outcome=AnalysisOutcome.IMPOSSIBLE.value,
```

**Nhãn:** L575

**Mô tả:** Hành vi dòng 575.

**Vị trí file:** `pipeline.py` dòng 575 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 575; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.570 — Dòng 576: `caveats=[iv_parsed.explanation_vi or iv_parsed.reason or ""]...`

```python
                        caveats=[iv_parsed.explanation_vi or iv_parsed.reason or ""],
```

**Nhãn:** L576

**Mô tả:** Hành vi dòng 576.

**Vị trí file:** `pipeline.py` dòng 576 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 576; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.571 — Dòng 577: `empty_reason=iv_parsed.impossible_reason,`

```python
                        empty_reason=iv_parsed.impossible_reason,
```

**Nhãn:** L577

**Mô tả:** Hành vi dòng 577.

**Vị trí file:** `pipeline.py` dòng 577 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 577; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.572 — Dòng 578: `),`

```python
                    ),
```

**Nhãn:** L578

**Mô tả:** Hành vi dòng 578.

**Vị trí file:** `pipeline.py` dòng 578 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 578; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.573 — Dòng 579: `)`

```python
                )
```

**Nhãn:** L579

**Mô tả:** Hành vi dòng 579.

**Vị trí file:** `pipeline.py` dòng 579 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 579; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.574 — Dòng 580: ``

```python

```

**Nhãn:** L580

**Mô tả:** Hành vi dòng 580.

**Vị trí file:** `pipeline.py` dòng 580 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 580; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.575 — Dòng 581: `if iv_action in {"complete", "partial"}:`

```python
            if iv_action in {"complete", "partial"}:
```

**Nhãn:** complete partial

**Mô tả:** iv_action in complete partial.

**Vị trí file:** `pipeline.py` dòng 581 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 581; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.576 — Dòng 582: `if iv_parsed.sandbox_steps:`

```python
                if iv_parsed.sandbox_steps:
```

**Nhãn:** L582

**Mô tả:** Hành vi dòng 582.

**Vị trí file:** `pipeline.py` dòng 582 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 582; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.577 — Dòng 583: `workflow.steps.append(`

```python
                    workflow.steps.append(
```

**Nhãn:** L583

**Mô tả:** Hành vi dòng 583.

**Vị trí file:** `pipeline.py` dòng 583 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 583; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.578 — Dòng 584: `WorkflowStep(`

```python
                        WorkflowStep(
```

**Nhãn:** L584

**Mô tả:** Hành vi dòng 584.

**WorkflowStep:** step_id UUID mới; orchestrator persist workflow qua Redis sau run.

**Vị trí file:** `pipeline.py` dòng 584 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 584; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.579 — Dòng 585: `step_id=str(uuid4()),`

```python
                            step_id=str(uuid4()),
```

**Nhãn:** L585

**Mô tả:** Hành vi dòng 585.

**Vị trí file:** `pipeline.py` dòng 585 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 585; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.580 — Dòng 586: `trace_id=trace_id,`

```python
                            trace_id=trace_id,
```

**Nhãn:** L586

**Mô tả:** Hành vi dòng 586.

**Vị trí file:** `pipeline.py` dòng 586 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 586; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.581 — Dòng 587: `analysis_id=workflow.active_analysis_id or trace_id,`

```python
                            analysis_id=workflow.active_analysis_id or trace_id,
```

**Nhãn:** L587

**Mô tả:** Hành vi dòng 587.

**Vị trí file:** `pipeline.py` dòng 587 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 587; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.582 — Dòng 588: `step_type=WorkflowStepType.SANDBOX,`

```python
                            step_type=WorkflowStepType.SANDBOX,
```

**Nhãn:** L588

**Mô tả:** Hành vi dòng 588.

**Vị trí file:** `pipeline.py` dòng 588 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 588; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.583 — Dòng 589: `sql_attempt=sql_attempt,`

```python
                            sql_attempt=sql_attempt,
```

**Nhãn:** L589

**Mô tả:** Hành vi dòng 589.

**Vị trí file:** `pipeline.py` dòng 589 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 589; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.584 — Dòng 590: `summary=f"steps={iv_parsed.sandbox_steps}",`

```python
                            summary=f"steps={iv_parsed.sandbox_steps}",
```

**Nhãn:** L590

**Mô tả:** Hành vi dòng 590.

**Vị trí file:** `pipeline.py` dòng 590 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 590; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.585 — Dòng 591: `)`

```python
                        )
```

**Nhãn:** L591

**Mô tả:** Hành vi dòng 591.

**Vị trí file:** `pipeline.py` dòng 591 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 591; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.586 — Dòng 592: `)`

```python
                    )
```

**Nhãn:** L592

**Mô tả:** Hành vi dòng 592.

**Vị trí file:** `pipeline.py` dòng 592 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 592; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.587 — Dòng 593: `workflow.progress_step = WorkflowStepType.SYNTHESIZE.value`

```python
                workflow.progress_step = WorkflowStepType.SYNTHESIZE.value
```

**Nhãn:** L593

**Mô tả:** Hành vi dòng 593.

**Vị trí file:** `pipeline.py` dòng 593 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 593; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.588 — Dòng 594: `self._emit_progress(workflow, on_progress)`

```python
                self._emit_progress(workflow, on_progress)
```

**Nhãn:** L594

**Mô tả:** Hành vi dòng 594.

**Vị trí file:** `pipeline.py` dòng 594 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 594; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.589 — Dòng 595: `artifact_paths = iv_parsed.artifact_paths`

```python
                artifact_paths = iv_parsed.artifact_paths
```

**Nhãn:** L595

**Mô tả:** Hành vi dòng 595.

**Vị trí file:** `pipeline.py` dòng 595 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 595; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.590 — Dòng 596: `coverage = iv_parsed.coverage`

```python
                coverage = iv_parsed.coverage
```

**Nhãn:** L596

**Mô tả:** Hành vi dòng 596.

**Vị trí file:** `pipeline.py` dòng 596 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 596; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.591 — Dòng 597: `outcome = AnalysisOutcome.SUCCESS if iv_action == "complete"...`

```python
                outcome = AnalysisOutcome.SUCCESS if iv_action == "complete" else AnalysisOutcome.PARTIAL
```

**Nhãn:** L597

**Mô tả:** Hành vi dòng 597.

**Vị trí file:** `pipeline.py` dòng 597 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 597; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.592 — Dòng 598: `summary = TechnicalSummary(`

```python
                summary = TechnicalSummary(
```

**Nhãn:** L598

**Mô tả:** Hành vi dòng 598.

**Vị trí file:** `pipeline.py` dòng 598 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 598; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.593 — Dòng 599: `outcome=outcome.value,`

```python
                    outcome=outcome.value,
```

**Nhãn:** L599

**Mô tả:** Hành vi dòng 599.

**Vị trí file:** `pipeline.py` dòng 599 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 599; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.594 — Dòng 600: `headline_metrics=iv_parsed.headline_metrics,`

```python
                    headline_metrics=iv_parsed.headline_metrics,
```

**Nhãn:** L600

**Mô tả:** Hành vi dòng 600.

**Vị trí file:** `pipeline.py` dòng 600 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 600; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.595 — Dòng 601: `artifact_urls=[str(out_dir / Path(p).name) for p in artifact...`

```python
                    artifact_urls=[str(out_dir / Path(p).name) for p in artifact_paths],
```

**Nhãn:** L601

**Mô tả:** Hành vi dòng 601.

**Vị trí file:** `pipeline.py` dòng 601 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 601; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.596 — Dòng 602: `caveats=iv_parsed.caveats,`

```python
                    caveats=iv_parsed.caveats,
```

**Nhãn:** L602

**Mô tả:** Hành vi dòng 602.

**Vị trí file:** `pipeline.py` dòng 602 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 602; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.597 — Dòng 603: `coverage=coverage,`

```python
                    coverage=coverage,
```

**Nhãn:** L603

**Mô tả:** Hành vi dòng 603.

**Vị trí file:** `pipeline.py` dòng 603 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 603; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.598 — Dòng 604: `)`

```python
                )
```

**Nhãn:** L604

**Mô tả:** Hành vi dòng 604.

**Vị trí file:** `pipeline.py` dòng 604 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 604; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.599 — Dòng 605: `if self.analysis_tool_registry:`

```python
                if self.analysis_tool_registry:
```

**Nhãn:** L605

**Mô tả:** Hành vi dòng 605.

**Vị trí file:** `pipeline.py` dòng 605 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 605; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.600 — Dòng 606: `for step_raw in iv_parsed.new_steps:`

```python
                    for step_raw in iv_parsed.new_steps:
```

**Nhãn:** L606

**Mô tả:** Hành vi dòng 606.

**Vị trí file:** `pipeline.py` dòng 606 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 606; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.601 — Dòng 607: `from project_core.domain.contracts.analysis_plan import Reci...`

```python
                        from project_core.domain.contracts.analysis_plan import RecipeStep
```

**Nhãn:** L607

**Mô tả:** Hành vi dòng 607.

**Vị trí file:** `pipeline.py` dòng 607 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 607; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.602 — Dòng 608: ``

```python

```

**Nhãn:** L608

**Mô tả:** Hành vi dòng 608.

**Vị trí file:** `pipeline.py` dòng 608 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 608; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.603 — Dòng 609: `step = RecipeStep.model_validate(step_raw)`

```python
                        step = RecipeStep.model_validate(step_raw)
```

**Nhãn:** L609

**Mô tả:** Hành vi dòng 609.

**Vị trí file:** `pipeline.py` dòng 609 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 609; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.604 — Dòng 610: `self.analysis_tool_registry.stage_step(`

```python
                        self.analysis_tool_registry.stage_step(
```

**Nhãn:** L610

**Mô tả:** Hành vi dòng 610.

**Vị trí file:** `pipeline.py` dòng 610 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 610; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.605 — Dòng 611: `step=step,`

```python
                            step=step,
```

**Nhãn:** L611

**Mô tả:** Hành vi dòng 611.

**Vị trí file:** `pipeline.py` dòng 611 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 611; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.606 — Dòng 612: `intent=brief.intent,`

```python
                            intent=brief.intent,
```

**Nhãn:** L612

**Mô tả:** Hành vi dòng 612.

**Vị trí file:** `pipeline.py` dòng 612 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 612; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.607 — Dòng 613: `trace_id=trace_id,`

```python
                            trace_id=trace_id,
```

**Nhãn:** L613

**Mô tả:** Hành vi dòng 613.

**Vị trí file:** `pipeline.py` dòng 613 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 613; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.608 — Dòng 614: `)`

```python
                        )
```

**Nhãn:** L614

**Mô tả:** Hành vi dòng 614.

**Vị trí file:** `pipeline.py` dòng 614 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 614; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.609 — Dòng 615: `if iv_parsed.analysis_script and not iv_parsed.new_steps:`

```python
                    if iv_parsed.analysis_script and not iv_parsed.new_steps:
```

**Nhãn:** L615

**Mô tả:** Hành vi dòng 615.

**Vị trí file:** `pipeline.py` dòng 615 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 615; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.610 — Dòng 616: `self.analysis_tool_registry.stage_from_run(`

```python
                        self.analysis_tool_registry.stage_from_run(
```

**Nhãn:** L616

**Mô tả:** Hành vi dòng 616.

**Vị trí file:** `pipeline.py` dòng 616 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 616; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.611 — Dòng 617: `name=f"analysis_{trace_id[:8]}",`

```python
                            name=f"analysis_{trace_id[:8]}",
```

**Nhãn:** L617

**Mô tả:** Hành vi dòng 617.

**Vị trí file:** `pipeline.py` dòng 617 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 617; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.612 — Dòng 618: `intent=brief.intent,`

```python
                            intent=brief.intent,
```

**Nhãn:** L618

**Mô tả:** Hành vi dòng 618.

**Vị trí file:** `pipeline.py` dòng 618 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 618; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.613 — Dòng 619: `script=iv_parsed.analysis_script,`

```python
                            script=iv_parsed.analysis_script,
```

**Nhãn:** L619

**Mô tả:** Hành vi dòng 619.

**Vị trí file:** `pipeline.py` dòng 619 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 619; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.614 — Dòng 620: `trace_id=trace_id,`

```python
                            trace_id=trace_id,
```

**Nhãn:** L620

**Mô tả:** Hành vi dòng 620.

**Vị trí file:** `pipeline.py` dòng 620 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 620; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.615 — Dòng 621: `datasets=[q.model_dump() for q in query_files],`

```python
                            datasets=[q.model_dump() for q in query_files],
```

**Nhãn:** L621

**Mô tả:** Hành vi dòng 621.

**model_dump:** JSON-serializable cho HTTP agent; permissions dùng mode="json".

**Vị trí file:** `pipeline.py` dòng 621 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 621; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.616 — Dòng 622: `artifacts=artifact_paths,`

```python
                            artifacts=artifact_paths,
```

**Nhãn:** L622

**Mô tả:** Hành vi dòng 622.

**Vị trí file:** `pipeline.py` dòng 622 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 622; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.617 — Dòng 623: `metrics=summary.headline_metrics,`

```python
                            metrics=summary.headline_metrics,
```

**Nhãn:** L623

**Mô tả:** Hành vi dòng 623.

**Vị trí file:** `pipeline.py` dòng 623 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 623; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.618 — Dòng 624: `)`

```python
                        )
```

**Nhãn:** L624

**Mô tả:** Hành vi dòng 624.

**Vị trí file:** `pipeline.py` dòng 624 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 624; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.619 — Dòng 625: `if self.feedback_loop is not None:`

```python
                if self.feedback_loop is not None:
```

**Nhãn:** L625

**Mô tả:** Hành vi dòng 625.

**Vị trí file:** `pipeline.py` dòng 625 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 625; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.620 — Dòng 626: `self.feedback_loop.on_pipeline_complete(`

```python
                    self.feedback_loop.on_pipeline_complete(
```

**Nhãn:** L626

**Mô tả:** Hành vi dòng 626.

**Vị trí file:** `pipeline.py` dòng 626 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 626; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.621 — Dòng 627: `trace_id,`

```python
                        trace_id,
```

**Nhãn:** L627

**Mô tả:** Hành vi dòng 627.

**Vị trí file:** `pipeline.py` dòng 627 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 627; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.622 — Dòng 628: `outcome.value,`

```python
                        outcome.value,
```

**Nhãn:** L628

**Mô tả:** Hành vi dòng 628.

**Vị trí file:** `pipeline.py` dòng 628 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 628; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.623 — Dòng 629: `trace_artifacts={`

```python
                        trace_artifacts={
```

**Nhãn:** L629

**Mô tả:** Hành vi dòng 629.

**Vị trí file:** `pipeline.py` dòng 629 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 629; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.624 — Dòng 630: `"brief": brief,`

```python
                            "brief": brief,
```

**Nhãn:** L630

**Mô tả:** Hành vi dòng 630.

**Vị trí file:** `pipeline.py` dòng 630 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 630; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.625 — Dòng 631: `"approved_sql": approved_sql,`

```python
                            "approved_sql": approved_sql,
```

**Nhãn:** L631

**Mô tả:** Hành vi dòng 631.

**Vị trí file:** `pipeline.py` dòng 631 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 631; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.626 — Dòng 632: `"sql_attempt": sql_attempt,`

```python
                            "sql_attempt": sql_attempt,
```

**Nhãn:** L632

**Mô tả:** Hành vi dòng 632.

**Vị trí file:** `pipeline.py` dòng 632 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 632; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.627 — Dòng 633: `"correction_path": sql_attempt > 1,`

```python
                            "correction_path": sql_attempt > 1,
```

**Nhãn:** L633

**Mô tả:** Hành vi dòng 633.

**Vị trí file:** `pipeline.py` dòng 633 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 633; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.628 — Dòng 634: `"artifact_paths": summary.artifact_urls,`

```python
                            "artifact_paths": summary.artifact_urls,
```

**Nhãn:** L634

**Mô tả:** Hành vi dòng 634.

**Vị trí file:** `pipeline.py` dòng 634 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 634; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.629 — Dòng 635: `"headline_metrics": summary.headline_metrics,`

```python
                            "headline_metrics": summary.headline_metrics,
```

**Nhãn:** L635

**Mô tả:** Hành vi dòng 635.

**Vị trí file:** `pipeline.py` dòng 635 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 635; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.630 — Dòng 636: `"analysis_id": workflow.active_analysis_id or trace_id,`

```python
                            "analysis_id": workflow.active_analysis_id or trace_id,
```

**Nhãn:** L636

**Mô tả:** Hành vi dòng 636.

**Vị trí file:** `pipeline.py` dòng 636 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 636; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.631 — Dòng 637: `"actor_id": permissions.actor_id,`

```python
                            "actor_id": permissions.actor_id,
```

**Nhãn:** L637

**Mô tả:** Hành vi dòng 637.

**Vị trí file:** `pipeline.py` dòng 637 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 637; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.632 — Dòng 638: `"workflow_steps": workflow.steps,`

```python
                            "workflow_steps": workflow.steps,
```

**Nhãn:** L638

**Mô tả:** Hành vi dòng 638.

**Vị trí file:** `pipeline.py` dòng 638 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 638; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.633 — Dòng 639: `"analysis_script": iv_parsed.analysis_script,`

```python
                            "analysis_script": iv_parsed.analysis_script,
```

**Nhãn:** L639

**Mô tả:** Hành vi dòng 639.

**Vị trí file:** `pipeline.py` dòng 639 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 639; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.634 — Dòng 640: `},`

```python
                        },
```

**Nhãn:** L640

**Mô tả:** Hành vi dòng 640.

**Vị trí file:** `pipeline.py` dòng 640 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 640; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.635 — Dòng 641: `)`

```python
                    )
```

**Nhãn:** L641

**Mô tả:** Hành vi dòng 641.

**Vị trí file:** `pipeline.py` dòng 641 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 641; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.636 — Dòng 642: `return self._finish(trace_id, workflow, outcome, summary)`

```python
                return self._finish(trace_id, workflow, outcome, summary)
```

**Nhãn:** L642

**Mô tả:** Hành vi dòng 642.

**_finish:** workflow IDLE, last_outcome, PipelineResult không needs_clarification.

**Vị trí file:** `pipeline.py` dòng 642 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 642; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.637 — Dòng 643: ``

```python

```

**Nhãn:** L643

**Mô tả:** Hành vi dòng 643.

**Vị trí file:** `pipeline.py` dòng 643 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 643; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.638 — Dòng 644: `return self._finish(`

```python
        return self._finish(
```

**Nhãn:** exhausted

**Mô tả:** Sau hết vòng sql_attempt ERROR exhausted.

**_finish:** workflow IDLE, last_outcome, PipelineResult không needs_clarification.

**Vị trí file:** `pipeline.py` dòng 644 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 644; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.639 — Dòng 645: `trace_id,`

```python
            trace_id,
```

**Nhãn:** L645

**Mô tả:** Hành vi dòng 645.

**Vị trí file:** `pipeline.py` dòng 645 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 645; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.640 — Dòng 646: `workflow,`

```python
            workflow,
```

**Nhãn:** L646

**Mô tả:** Hành vi dòng 646.

**Vị trí file:** `pipeline.py` dòng 646 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 646; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.641 — Dòng 647: `AnalysisOutcome.ERROR,`

```python
            AnalysisOutcome.ERROR,
```

**Nhãn:** L647

**Mô tả:** Hành vi dòng 647.

**Vị trí file:** `pipeline.py` dòng 647 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 647; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.642 — Dòng 648: `TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveat...`

```python
            TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveats=["pipeline exhausted"]),
```

**Nhãn:** L648

**Mô tả:** Hành vi dòng 648.

**Vị trí file:** `pipeline.py` dòng 648 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 648; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.643 — Dòng 649: `)`

```python
        )
```

**Nhãn:** L649

**Mô tả:** Hành vi dòng 649.

**Vị trí file:** `pipeline.py` dòng 649 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 649; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.644 — Dòng 650: ``

```python

```

**Nhãn:** L650

**Mô tả:** Hành vi dòng 650.

**Vị trí file:** `pipeline.py` dòng 650 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 650; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.645 — Dòng 651: `@staticmethod`

```python
    @staticmethod
```

**Nhãn:** L651

**Mô tả:** Hành vi dòng 651.

**Vị trí file:** `pipeline.py` dòng 651 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 651; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.646 — Dòng 652: `def _deadline_exceeded(deadline: float | None) -> bool:`

```python
    def _deadline_exceeded(deadline: float | None) -> bool:
```

**Nhãn:** L652

**Mô tả:** Hành vi dòng 652.

**Vị trí file:** `pipeline.py` dòng 652 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 652; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.647 — Dòng 653: `return deadline is not None and time.monotonic() > deadline`

```python
        return deadline is not None and time.monotonic() > deadline
```

**Nhãn:** L653

**Mô tả:** Hành vi dòng 653.

**Vị trí file:** `pipeline.py` dòng 653 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 653; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.648 — Dòng 654: ``

```python

```

**Nhãn:** L654

**Mô tả:** Hành vi dòng 654.

**Vị trí file:** `pipeline.py` dòng 654 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 654; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.649 — Dòng 655: `@staticmethod`

```python
    @staticmethod
```

**Nhãn:** L655

**Mô tả:** Hành vi dòng 655.

**Vị trí file:** `pipeline.py` dòng 655 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 655; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.650 — Dòng 656: `def _emit_progress(workflow: WorkflowState, on_progress: Cal...`

```python
    def _emit_progress(workflow: WorkflowState, on_progress: Callable[[WorkflowState], None] | None) -> None:
```

**Nhãn:** L656

**Mô tả:** Hành vi dòng 656.

**Vị trí file:** `pipeline.py` dòng 656 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 656; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.651 — Dòng 657: `if on_progress is not None:`

```python
        if on_progress is not None:
```

**Nhãn:** L657

**Mô tả:** Hành vi dòng 657.

**Vị trí file:** `pipeline.py` dòng 657 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 657; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.652 — Dòng 658: `on_progress(workflow)`

```python
            on_progress(workflow)
```

**Nhãn:** L658

**Mô tả:** Hành vi dòng 658.

**Vị trí file:** `pipeline.py` dòng 658 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 658; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.653 — Dòng 659: ``

```python

```

**Nhãn:** L659

**Mô tả:** Hành vi dòng 659.

**Vị trí file:** `pipeline.py` dòng 659 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 659; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.654 — Dòng 660: `def _finish(`

```python
    def _finish(
```

**Nhãn:** L660

**Mô tả:** Hành vi dòng 660.

**Vị trí file:** `pipeline.py` dòng 660 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 660; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.655 — Dòng 661: `self,`

```python
        self,
```

**Nhãn:** L661

**Mô tả:** Hành vi dòng 661.

**Vị trí file:** `pipeline.py` dòng 661 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 661; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.656 — Dòng 662: `trace_id: str,`

```python
        trace_id: str,
```

**Nhãn:** L662

**Mô tả:** Hành vi dòng 662.

**Vị trí file:** `pipeline.py` dòng 662 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 662; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.657 — Dòng 663: `workflow: WorkflowState,`

```python
        workflow: WorkflowState,
```

**Nhãn:** L663

**Mô tả:** Hành vi dòng 663.

**Vị trí file:** `pipeline.py` dòng 663 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 663; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.658 — Dòng 664: `outcome: AnalysisOutcome,`

```python
        outcome: AnalysisOutcome,
```

**Nhãn:** L664

**Mô tả:** Hành vi dòng 664.

**Vị trí file:** `pipeline.py` dòng 664 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 664; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.659 — Dòng 665: `summary: TechnicalSummary,`

```python
        summary: TechnicalSummary,
```

**Nhãn:** L665

**Mô tả:** Hành vi dòng 665.

**Vị trí file:** `pipeline.py` dòng 665 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 665; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.660 — Dòng 666: `) -> PipelineResult:`

```python
    ) -> PipelineResult:
```

**Nhãn:** L666

**Mô tả:** Hành vi dòng 666.

**Vị trí file:** `pipeline.py` dòng 666 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 666; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.661 — Dòng 667: `workflow.status = WorkflowStatus.IDLE`

```python
        workflow.status = WorkflowStatus.IDLE
```

**Nhãn:** L667

**Mô tả:** Hành vi dòng 667.

**Vị trí file:** `pipeline.py` dòng 667 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 667; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.662 — Dòng 668: `workflow.last_outcome = outcome.value`

```python
        workflow.last_outcome = outcome.value
```

**Nhãn:** L668

**Mô tả:** Hành vi dòng 668.

**Vị trí file:** `pipeline.py` dòng 668 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 668; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.663 — Dòng 669: `workflow.last_completed_trace_id = trace_id`

```python
        workflow.last_completed_trace_id = trace_id
```

**Nhãn:** L669

**Mô tả:** Hành vi dòng 669.

**Vị trí file:** `pipeline.py` dòng 669 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 669; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.664 — Dòng 670: `workflow.progress_step = None`

```python
        workflow.progress_step = None
```

**Nhãn:** L670

**Mô tả:** Hành vi dòng 670.

**Vị trí file:** `pipeline.py` dòng 670 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 670; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.665 — Dòng 671: `return PipelineResult(`

```python
        return PipelineResult(
```

**Nhãn:** L671

**Mô tả:** Hành vi dòng 671.

**Vị trí file:** `pipeline.py` dòng 671 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 671; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.666 — Dòng 672: `trace_id=trace_id,`

```python
            trace_id=trace_id,
```

**Nhãn:** L672

**Mô tả:** Hành vi dòng 672.

**Vị trí file:** `pipeline.py` dòng 672 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 672; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.667 — Dòng 673: `analysis_id=workflow.active_analysis_id or trace_id,`

```python
            analysis_id=workflow.active_analysis_id or trace_id,
```

**Nhãn:** L673

**Mô tả:** Hành vi dòng 673.

**Vị trí file:** `pipeline.py` dòng 673 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 673; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.668 — Dòng 674: `outcome=outcome.value,`

```python
            outcome=outcome.value,
```

**Nhãn:** L674

**Mô tả:** Hành vi dòng 674.

**Vị trí file:** `pipeline.py` dòng 674 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 674; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.669 — Dòng 675: `technical_summary=summary,`

```python
            technical_summary=summary,
```

**Nhãn:** L675

**Mô tả:** Hành vi dòng 675.

**Vị trí file:** `pipeline.py` dòng 675 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 675; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.670 — Dòng 676: `workflow_steps=workflow.steps,`

```python
            workflow_steps=workflow.steps,
```

**Nhãn:** L676

**Mô tả:** Hành vi dòng 676.

**Vị trí file:** `pipeline.py` dòng 676 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 676; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.671 — Dòng 677: `)`

```python
        )
```

**Nhãn:** L677

**Mô tả:** Hành vi dòng 677.

**Vị trí file:** `pipeline.py` dòng 677 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 677; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.672 — Dòng 678: ``

```python

```

**Nhãn:** L678

**Mô tả:** Hành vi dòng 678.

**Vị trí file:** `pipeline.py` dòng 678 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 678; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.673 — Dòng 679: `@staticmethod`

```python
    @staticmethod
```

**Nhãn:** L679

**Mô tả:** Hành vi dòng 679.

**Vị trí file:** `pipeline.py` dòng 679 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 679; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.674 — Dòng 680: `def _merge_profiles(profiles: list[ResultProfile]) -> Result...`

```python
    def _merge_profiles(profiles: list[ResultProfile]) -> ResultProfile:
```

**Nhãn:** L680

**Mô tả:** Hành vi dòng 680.

**Vị trí file:** `pipeline.py` dòng 680 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 680; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.675 — Dòng 681: `if not profiles:`

```python
        if not profiles:
```

**Nhãn:** L681

**Mô tả:** Hành vi dòng 681.

**Vị trí file:** `pipeline.py` dòng 681 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 681; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.676 — Dòng 682: `return ResultProfile()`

```python
            return ResultProfile()
```

**Nhãn:** L682

**Mô tả:** Hành vi dòng 682.

**Vị trí file:** `pipeline.py` dòng 682 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 682; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.677 — Dòng 683: `total_rows = sum(p.row_count for p in profiles)`

```python
        total_rows = sum(p.row_count for p in profiles)
```

**Nhãn:** L683

**Mô tả:** Hành vi dòng 683.

**Vị trí file:** `pipeline.py` dòng 683 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 683; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.678 — Dòng 684: `flags: list[str] = []`

```python
        flags: list[str] = []
```

**Nhãn:** L684

**Mô tả:** Hành vi dòng 684.

**Vị trí file:** `pipeline.py` dòng 684 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 684; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.679 — Dòng 685: `if total_rows == 0:`

```python
        if total_rows == 0:
```

**Nhãn:** L685

**Mô tả:** Hành vi dòng 685.

**Vị trí file:** `pipeline.py` dòng 685 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 685; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.680 — Dòng 686: `flags.append("empty")`

```python
            flags.append("empty")
```

**Nhãn:** L686

**Mô tả:** Hành vi dòng 686.

**Vị trí file:** `pipeline.py` dòng 686 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 686; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.681 — Dòng 687: `return ResultProfile(row_count=total_rows, columns=profiles[...`

```python
        return ResultProfile(row_count=total_rows, columns=profiles[0].columns, flags=flags)
```

**Nhãn:** L687

**Mô tả:** Hành vi dòng 687.

**Vị trí file:** `pipeline.py` dòng 687 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 687; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.682 — Dòng 688: ``

```python

```

**Nhãn:** L688

**Mô tả:** Hành vi dòng 688.

**Vị trí file:** `pipeline.py` dòng 688 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 688; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.683 — Dòng 689: ``

```python

```

**Nhãn:** L689

**Mô tả:** Hành vi dòng 689.

**Vị trí file:** `pipeline.py` dòng 689 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 689; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.684 — Dòng 690: `def _needs_explain_from_feedback(risk_feedback: Any) -> bool...`

```python
def _needs_explain_from_feedback(risk_feedback: Any) -> bool:
```

**Nhãn:** L690

**Mô tả:** Hành vi dòng 690.

**Vị trí file:** `pipeline.py` dòng 690 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 690; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.685 — Dòng 691: `if not risk_feedback or not isinstance(risk_feedback, dict):`

```python
    if not risk_feedback or not isinstance(risk_feedback, dict):
```

**Nhãn:** L691

**Mô tả:** Hành vi dòng 691.

**Vị trí file:** `pipeline.py` dòng 691 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 691; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.686 — Dòng 692: `return False`

```python
        return False
```

**Nhãn:** L692

**Mô tả:** Hành vi dòng 692.

**Vị trí file:** `pipeline.py` dòng 692 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 692; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.687 — Dòng 693: `issue = str(risk_feedback.get("issue", "")).lower()`

```python
    issue = str(risk_feedback.get("issue", "")).lower()
```

**Nhãn:** L693

**Mô tả:** Hành vi dòng 693.

**Vị trí file:** `pipeline.py` dòng 693 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 693; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.688 — Dòng 694: `return any(k in issue for k in ("performance", "scan", "slow...`

```python
    return any(k in issue for k in ("performance", "scan", "slow", "full table"))
```

**Nhãn:** L694

**Mô tả:** Hành vi dòng 694.

**Vị trí file:** `pipeline.py` dòng 694 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 694; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.689 — Dòng 695: ``

```python

```

**Nhãn:** L695

**Mô tả:** Hành vi dòng 695.

**Vị trí file:** `pipeline.py` dòng 695 trong method `run` hoặc helper.

**Đối chiếu §Z.2.6:** Khối tóm tắt chứa dòng 695; Z.3 bóc chi tiết từng dòng.

**Kiểm thử:** `test_pipeline_flows`, `test_context_policy_pipeline`, `test_session_budget`.


### §Z.3.690 — Phân tích sâu `_deadline_exceeded` (651–653)

| Dòng | Giải thích |
|------|------------|
| 651 | `@staticmethod` — không cần instance |
| 652 | `deadline: float | None` — None → không bao giờ exceeded |
| 653 | `monotonic() > deadline` — strict greater; đúng deadline vẫn OK |

Gọi tại 120 đầu mỗi sql_attempt.

### §Z.3.691 — Phân tích sâu `_emit_progress` (655–658)

No-op nếu on_progress None. Ngược lại gọi on_progress(workflow) với progress_step đã set.

Điểm gọi: 150, 242, 362, 438, 594.

### §Z.3.692 — Phân tích sâu `_finish` (660–677)

Set workflow IDLE, last_outcome, last_completed_trace_id, progress_step None.

Return PipelineResult — không có needs_clarification (khác return clarify trực tiếp).

### §Z.3.693 — Phân tích sâu `_merge_profiles` (679–686)

Rỗng → ResultProfile(). Sum row_count; flag empty nếu 0; columns từ profile đầu.

Edge: multi-query khác schema — columns chỉ query 0; IV đọc từng parquet.

### §Z.3.694 — Phân tích sâu `_needs_explain_from_feedback` (690–694)

Module function. False nếu không dict.

issue lowercase chứa performance/scan/slow/full table → True.

Kết hợp iii_parsed.needs_explain tại 298–301.

### §Z.3.695 — Ma trận nhánh action Agent II (180–223)

| action | exploration_mode | Hành vi |
|--------|------------------|---------|
| clarify | False | clarify_round++, NEEDS_CLARIFICATION hoặc raise |
| clarify | True | Bỏ block 182 |
| impossible | * | _finish IMPOSSIBLE |
| plan_sql / probe_sql | * | Vòng SQL |
| khác | * | continue sql_attempt |

### §Z.3.696 — Ma trận nhánh iv_action Agent IV (503–642)

| iv_action | Kết quả |
|-----------|---------|
| data_feedback | continue / impossible / clarify / probe_mode |
| suggest_clarify | NEEDS_CLARIFICATION |
| impossible | _finish IMPOSSIBLE |
| complete / partial | SUCCESS/PARTIAL _finish |

### §Z.3.697 — Luồng inbox qua các vòng

1. policy_feedback (254) — II đọc
2. risk_feedback (297) — III
3. explain_plan (304) — III 273
4. data_feedback (507) — apply 132
5. probe_mode (551)

### §Z.3.698 — Artifact paths và retention

- raw: `{artifacts.base_dir}/{trace_id}/raw/query_{idx}.parquet`
- out: IV ghi out_dir; artifact_urls = out_dir / basename
- approved_sql trong feedback_loop trace_artifacts

### §Z.3.699 — Tương tác ChatOrchestrator

Orchestrator 81–88 inject HttpAgentInvoker, HttpSqlGatewayClient, catalog, feedback, registry, domain_store.

`_run_pipeline_and_respond` build permissions, gọi pipeline.run, bắt ClarifyRoundsExceededError.

Pipeline không biết session_id Redis.

---

*Hết §Z.3 — Phân tích từng dòng pipeline.py. Tổng số dòng mục Z.3 mới thêm: 11347.*