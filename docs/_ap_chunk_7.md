## §W.1 — Test files trong packages/project-test

> **Phạm vi:** Inventory và mô tả pytest suite — unit (project_core, agents) và integration (gateway, pipeline, auth).

### §W.1.1 — Cấu trúc thư mục

```
packages/project-test/
  conftest.py          # fixtures: fake_redis, platform_config, pipeline_factory, …
  unit/project_core/   # domain, policy, pipeline helpers
  unit/agents/         # agent I–IV behavior
  integration/         # HTTP gateway, live DB, end-to-end pipeline
  src/project_test/helpers/  # stub_sql, llm_stub, fake_mongo, scripted_invoker
  fixtures/            # golden_supermarket.yaml
```

### §W.1.2 — `unit/project_core/`

#### `packages/project-test/unit/project_core/test_acl_context.py`

**Mục đích:** SqlAclContext từ PermissionsSnapshot.

**Test cases:**
- `test_store_manager_requires_store_filter()`
- `test_hq_analyst_has_broader_tables()`
- `test_context_policy_agent_II_gets_brief()`
- `test_context_policy_IV_sandbox_tools_only()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_acl_context.py -v`

#### `packages/project-test/unit/project_core/test_agent_intelligence.py`

**Mục đích:** Agent heuristic behaviors.

**Test cases:**
- `test_product_resolver_generates_probes()`
- `test_apply_data_feedback_sets_exploration()`
- `test_ingest_txt_file()`
- `test_iv_analyzer_empty_result()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_agent_intelligence.py -v`

#### `packages/project-test/unit/project_core/test_agent_output_parse.py`

**Mục đích:** Parse structured agent JSON output.

**Test cases:**
- `test_parse_agent_ii_valid()`
- `test_parse_agent_iii_invalid_verdict()`
- `test_parse_agent_iv_missing_action()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_agent_output_parse.py -v`

#### `packages/project-test/unit/project_core/test_brief_templates.py`

**Mục đích:** Template rendering cho analysis brief.

**Test cases:**
- `test_brief_templates_excerpt_not_empty()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_brief_templates.py -v`

#### `packages/project-test/unit/project_core/test_budget.py`

**Mục đích:** BudgetGuard token caps per agent.

**Test cases:**
- `test_budget_records_agent_calls()`
- `test_budget_exceeds_agent_cap_raises()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_budget.py -v`

#### `packages/project-test/unit/project_core/test_catalog_policy.py`

**Mục đích:** Schema catalog policy filters.

**Test cases:**
- `test_sql_table_names_include_shards()`
- `test_policy_blocks_non_dictionary_table()`
- `test_policy_allows_dictionary_table()`
- `test_policy_blocks_delete()`
- `test_store_manager_cannot_query_hissppr()`
- `test_agent_schema_bundle_has_descriptions()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_catalog_policy.py -v`

#### `packages/project-test/unit/project_core/test_clarification.py`

**Mục đích:** ClarificationCoordinator rounds + suspend.

**Test cases:**
- `test_bridge_resolves_vip_from_transcript()`
- `test_bridge_ask_user_when_transcript_insufficient()`
- `test_apply_clarification_reply_updates_brief()`
- `test_enforce_clarify_source_II_only()`
- `test_can_emit_clarify_within_round_cap()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_clarification.py -v`

#### `packages/project-test/unit/project_core/test_clarification_bridge.py`

**Mục đích:** Agent I bridge confidence threshold.

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_clarification_bridge.py -v`

#### `packages/project-test/unit/project_core/test_compose_analysis.py`

**Mục đích:** Brief composition templates.

**Test cases:**
- `test_decompose_macro_intent()`
- `test_rank_candidates_partial_match()`
- `test_build_execution_plan_reuse_and_generate()`
- `test_resolve_params_from_brief_filters()`
- `test_hybrid_rank_prefers_embedding_overlap()`
- `test_select_recipe_stub_picks_top_candidate()`
- `test_registry_mcp_descriptors_and_invoke()`
- `test_decompose_heuristic_unchanged_with_stub()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_compose_analysis.py -v`

#### `packages/project-test/unit/project_core/test_context_policy_pipeline.py`

**Mục đích:** Pipeline + policy integration unit.

**Test cases:**
- `test_filter_schema_excerpt_respects_allowed_tables()`
- `test_is_tool_allowed_per_agent()`
- `test_can_invoke_tool_respects_grants()`
- `test_tool_wildcard_grant_matches_all()`
- `test_can_invoke_function_wildcard_and_specific()`
- `test_pipeline_explain_sql_on_performance_reject()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_context_policy_pipeline.py -v`

#### `packages/project-test/unit/project_core/test_contracts.py`

**Mục đích:** Pydantic contracts round-trip.

**Test cases:**
- `test_analysis_brief_roundtrip()`
- `test_intent_slice_from_brief()`
- `test_clarification_request_source_must_be_II()`
- `test_data_feedback_requires_issue_and_summary()`
- `test_workflow_state_defaults_idle()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_contracts.py -v`

#### `packages/project-test/unit/project_core/test_feedback_loop.py`

**Mục đích:** CaseStudyIndexer + FeedbackLoop Mongo.

**Test cases:**
- `test_on_pipeline_complete_stages_success()`
- `test_on_pipeline_complete_skips_impossible()`
- `test_on_user_feedback_promotes()`
- `test_on_satisfaction_signal_demotes()`
- `test_behavioral_signal_increases_promote_score()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_feedback_loop.py -v`

#### `packages/project-test/unit/project_core/test_iv_impossible.py`

**Mục đích:** Agent IV impossible outcome path.

**Test cases:**
- `test_is_impossible_for_unmappable_metric()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_iv_impossible.py -v`

#### `packages/project-test/unit/project_core/test_permission_set.py`

**Mục đích:** PermissionSet RBAC logic.

**Test cases:**
- `test_capability_granted_exact_and_wildcard()`
- `test_tool_capability_mapping()`
- `test_full_access_snapshot_expands_all_tables()`
- `test_restricted_snapshot_from_keys()`
- `test_user_permission_revoke_override()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_permission_set.py -v`

#### `packages/project-test/unit/project_core/test_policy_engine.py`

**Mục đích:** PolicyEngine validate SQL — joins, rows, denied columns.

**Test cases:**
- `test_policy_allows_select()`
- `test_policy_blocks_delete()`
- `test_policy_blocks_disallowed_table()`
- `test_policy_injects_row_limit()`
- `test_policy_store_filter_when_required()`
- `test_policy_blocks_semicolon_injection()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_policy_engine.py -v`

#### `packages/project-test/unit/project_core/test_schema_retrieval.py`

**Mục đích:** RAG schema chunks từ data_dictionary.

**Test cases:**
- `test_hybrid_retriever_merges_collections()`
- `test_schema_retriever_skips_status_filter()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_schema_retrieval.py -v`

#### `packages/project-test/unit/project_core/test_session_budget.py`

**Mục đích:** Session-level budget tracking qua pipeline.

**Test cases:**
- `test_session_budget_records_agent_i()`
- `test_session_budget_enforces_cap()`
- `test_pipeline_uses_shared_trace_budget()`
- `test_orchestrator_syncs_budget_spent()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_session_budget.py -v`

#### `packages/project-test/unit/project_core/test_shard_resolver.py`

**Mục đích:** STRANS_YYYYMM shard resolution.

**Test cases:**
- `test_rolling_cutoff_june_2026()`
- `test_shards_for_range_filters_by_month()`
- `test_suggest_query_plan_spanning_cutoff()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_shard_resolver.py -v`

#### `packages/project-test/unit/project_core/test_smoke.py`

**Mục đích:** Scaffold smoke — parse_duration, paths import.

**Test cases:**
- `test_parse_duration_60s()`
- `test_parse_duration_5m()`
- `test_paths_module_importable()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_smoke.py -v`

#### `packages/project-test/unit/project_core/test_tcvn3.py`

**Mục đích:** Vietnamese encoding TCVN3 samples.

**Test cases:**
- `test_sample_file_pairs()`
- `test_map_lengths_match()`
- `test_multi_char_sequence()`
- `test_single_char_d()`
- `test_remark_string_no_double_replace()`
- `test_copyright_to_circumflex()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_tcvn3.py -v`

#### `packages/project-test/unit/project_core/test_user_claims.py`

**Mục đích:** JWT claims → permissions mapping.

**Test cases:**
- `test_normalize_store_ids_empty_list()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_user_claims.py -v`

#### `packages/project-test/unit/project_core/test_workflow.py`

**Mục đích:** WorkflowState transitions, IDLE→ANALYSIS→COMPLETE.

**Test cases:**
- `test_start_analysis_resets_counters()`
- `test_suspend_and_resume_clarification()`
- `test_summarize_steps_and_detect_data_feedback()`

**Chạy:** `uv run pytest packages/project-test/unit/project_core/test_workflow.py -v`

### §W.1.3 — `unit/agents/`

#### `packages/project-test/unit/agents/test_agent_I.py`

**Mục đích:** Conversational router — ingress, synthesize.

**Test cases:**
- `test_ingress_routes_analysis_for_vip()`
- `test_ingress_chitchat()`
- `test_clarification_bridge_ask_user()`
- `test_clarify_mode_returns_mcq()`
- `test_synthesize_returns_outcome_message()`

**Chạy:** `uv run pytest packages/project-test/unit/agents/test_agent_I.py -v`

#### `packages/project-test/unit/agents/test_agent_II.py`

**Mục đích:** SQL planner — plan_sql, clarify, probe.

**Test cases:**
- `test_II_clarify_when_vip_ambiguous()`
- `test_II_plan_sql_after_filter_set()`
- `test_II_reads_policy_feedback_in_inbox()`
- `test_II_denied_without_permissions()`

**Chạy:** `uv run pytest packages/project-test/unit/agents/test_agent_II.py -v`

#### `packages/project-test/unit/agents/test_agent_III.py`

**Mục đích:** Risk reviewer — approve/reject/explain.

**Test cases:**
- `test_III_approves_safe_select()`
- `test_III_rejects_drop()`
- `test_III_denied_without_permissions()`

**Chạy:** `uv run pytest packages/project-test/unit/agents/test_agent_III.py -v`

#### `packages/project-test/unit/agents/test_agent_IV.py`

**Mục đích:** Data analyst — parquet analysis, sandbox.

**Test cases:**
- `test_IV_complete_with_rows()`
- `test_IV_data_feedback_when_empty()`
- `test_IV_artifact_paths_map_raw_to_out()`
- `test_IV_denied_without_permissions()`

**Chạy:** `uv run pytest packages/project-test/unit/agents/test_agent_IV.py -v`

#### `packages/project-test/unit/agents/test_circuit_breaker.py`

**Mục đích:** Circuit breaker khi agent down.

**Test cases:**
- `test_circuit_opens_after_failures()`
- `test_http_sql_gateway_fast_fail_when_open()`

**Chạy:** `uv run pytest packages/project-test/unit/agents/test_circuit_breaker.py -v`

#### `packages/project-test/unit/agents/test_orchestrator_feedback.py`

**Mục đích:** Orchestrator ↔ pipeline feedback.

**Test cases:**
- `test_satisfaction_signal_calls_feedback_loop()`
- `test_artifact_download_behavioral_signal()`

**Chạy:** `uv run pytest packages/project-test/unit/agents/test_orchestrator_feedback.py -v`

#### `packages/project-test/unit/agents/test_skill_bundles.py`

**Mục đích:** SKILL.md + TOOLS.md loading.

**Test cases:**
- `test_skill_bundle_loads()`
- `test_router_guides_exist()`
- `test_sql_planner_guides_exist()`
- `test_ingress_prompt_assembles()`

**Chạy:** `uv run pytest packages/project-test/unit/agents/test_skill_bundles.py -v`

### §W.1.4 — `integration/`

#### `packages/project-test/integration/test_agent_communication.py`

**Mục đích:** A2A message between agents.

**Test cases:**
- `test_communication_II_to_III_to_IV_order()`
- `test_communication_III_receives_sql_from_II()`
- `test_communication_IV_receives_dataset_manifest()`
- `test_communication_IV_to_II_data_feedback_inbox()`
- `test_communication_I_not_in_pipeline_invoke()`
- `test_communication_sql_gateway_executes_after_III_approve()`

**Chạy:** `uv run pytest packages/project-test/integration/test_agent_communication.py -v`

#### `packages/project-test/integration/test_auth_login.py`

**Mục đích:** AUTH login + JWT issuance.

**Test cases:**
- `test_normalize_store_ids_from_csv()`
- `test_claims_from_user_dict()`
- `test_bcrypt_roundtrip()`
- `test_store_manager_sql_acl_blocks_sensitive_column()`
- `test_password_login_endpoint()`

**Chạy:** `uv run pytest packages/project-test/integration/test_auth_login.py -v`

#### `packages/project-test/integration/test_chat_gateway.py`

**Mục đích:** Chat API — /chat, workflow poll.

**Test cases:**
- `test_health()`
- `test_dev_login_issues_token()`
- `test_chat_analysis_route()`
- `test_feedback_endpoint()`
- `test_analysis_status_endpoint()`

**Chạy:** `uv run pytest packages/project-test/integration/test_chat_gateway.py -v`

#### `packages/project-test/integration/test_error_paths.py`

**Mục đích:** HTTP 4xx/5xx error handling.

**Test cases:**
- `test_error_codes_have_stable_strings()`
- `test_clarify_rounds_exceeded_is_project_error()`
- `test_outcome_eligibility_matrix()`
- `test_satisfaction_negative_detected()`
- `test_satisfaction_positive_detected()`
- `test_result_profile_flags_empty()`
- `test_pipeline_IV_impossible_outcome()`
- `test_stub_sql_policy_block_path()`

**Chạy:** `uv run pytest packages/project-test/integration/test_error_paths.py -v`

#### `packages/project-test/integration/test_live_llm.py`

**Mục đích:** Live LLM (optional, no stub).

**Test cases:**
- `test_live_openrouter_ping()`

**Chạy:** `uv run pytest packages/project-test/integration/test_live_llm.py -v`

#### `packages/project-test/integration/test_live_sql.py`

**Mục đích:** Live SQL Server (optional CI).

**Test cases:**
- `test_live_sql_gateway_health()`

**Chạy:** `uv run pytest packages/project-test/integration/test_live_sql.py -v`

#### `packages/project-test/integration/test_orchestrator_wiring.py`

**Mục đích:** ChatOrchestrator + platform config wiring.

**Test cases:**
- `test_analysis_status_after_chat()`
- `test_analysis_status_not_found()`
- `test_re_ask_behavioral_after_negative_outcome()`

**Chạy:** `uv run pytest packages/project-test/integration/test_orchestrator_wiring.py -v`

#### `packages/project-test/integration/test_pipeline_deadline.py`

**Mục đích:** max_sync_seconds timeout behavior.

**Test cases:**
- `test_pipeline_sync_deadline_exceeded()`

**Chạy:** `uv run pytest packages/project-test/integration/test_pipeline_deadline.py -v`

#### `packages/project-test/integration/test_pipeline_explain.py`

**Mục đích:** EXPLAIN plan flow Agent III.

**Test cases:**
- `test_pipeline_explain_path()`

**Chạy:** `uv run pytest packages/project-test/integration/test_pipeline_explain.py -v`

#### `packages/project-test/integration/test_pipeline_explain_target_db.py`

**Mục đích:** Explain against target DB shard.

**Test cases:**
- `test_explain_sql_uses_query_target_db()`

**Chạy:** `uv run pytest packages/project-test/integration/test_pipeline_explain_target_db.py -v`

#### `packages/project-test/integration/test_pipeline_flows.py`

**Mục đích:** E2E pipeline happy/clarify/impossible paths.

**Test cases:**
- `test_pipeline_success_happy_path()`
- `test_pipeline_needs_clarification()`
- `test_pipeline_II_impossible()`
- `test_pipeline_risk_reject_then_retry()`
- `test_pipeline_IV_data_feedback_loop()`
- `test_pipeline_policy_blocked_exhausted()`
- `test_pipeline_clarify_rounds_exceeded()`
- `test_pipeline_stages_case_study_on_success()`

**Chạy:** `uv run pytest packages/project-test/integration/test_pipeline_flows.py -v`

#### `packages/project-test/integration/test_pipeline_progress.py`

**Mục đích:** on_progress callback steps.

**Test cases:**
- `test_pipeline_progress_callback()`

**Chạy:** `uv run pytest packages/project-test/integration/test_pipeline_progress.py -v`

#### `packages/project-test/integration/test_pipeline_stub.py`

**Mục đích:** Pipeline với stub invoker + SQL.

**Chạy:** `uv run pytest packages/project-test/integration/test_pipeline_stub.py -v`

#### `packages/project-test/integration/test_sandbox_tools.py`

**Mục đích:** Python sandbox MCP tools.

**Test cases:**
- `test_sandbox_load_dataset()`
- `test_sandbox_preview_dataframe()`
- `test_sandbox_export_excel()`
- `test_sandbox_plot_chart()`
- `test_sandbox_run_analysis_script()`
- `test_sandbox_missing_file_returns_error()`

**Chạy:** `uv run pytest packages/project-test/integration/test_sandbox_tools.py -v`

#### `packages/project-test/integration/test_security_regression.py`

**Mục đích:** Security regression suite.

**Test cases:**
- `test_agent_run_requires_token_when_auth_enabled()`
- `test_agent_run_with_valid_token()`
- `test_sandbox_escape_read_outside_dataset()`
- `test_sandbox_output_dir_outside_artifacts_rejected()`

**Chạy:** `uv run pytest packages/project-test/integration/test_security_regression.py -v`

#### `packages/project-test/integration/test_sql_audit.py`

**Mục đích:** Audit log SQL executions.

**Test cases:**
- `test_pipeline_emits_sql_execute_audit()`

**Chạy:** `uv run pytest packages/project-test/integration/test_sql_audit.py -v`

#### `packages/project-test/integration/test_sql_gateway.py`

**Mục đích:** SQL gateway HTTP — validate, execute.

**Test cases:**
- `test_validate_sql_allows_select()`
- `test_validate_sql_blocks_delete()`
- `test_get_schema_snapshot_has_tables()`
- `test_execute_readonly_without_dsn_returns_error_or_rows()`

**Chạy:** `uv run pytest packages/project-test/integration/test_sql_gateway.py -v`

#### `packages/project-test/integration/test_sql_gateway_acl_enforcement.py`

**Mục đích:** ACL deny column/table/store.

**Test cases:**
- `test_store_manager_blocked_on_forbidden_table()`
- `test_explain_sql_validates_before_plan()`
- `test_hq_analyst_allowed_select()`
- `test_empty_allowed_tables_denied_by_default()`
- `test_tool_gate_denies_when_no_grants()`
- `test_execute_denied_without_execute_tool_grant()`

**Chạy:** `uv run pytest packages/project-test/integration/test_sql_gateway_acl_enforcement.py -v`

#### `packages/project-test/integration/test_stm_gateway.py`

**Mục đích:** STM gateway session CRUD.

**Test cases:**
- `test_stm_save_and_load_transcript()`
- `test_stm_save_workflow()`
- `test_stm_clarification_roundtrip()`
- `test_stm_append_turn()`
- `test_stm_find_by_analysis_id()`

**Chạy:** `uv run pytest packages/project-test/integration/test_stm_gateway.py -v`

### §W.1.5 — Fixtures (conftest.py)

| Fixture | Mô tả |
|---------|-------|
| `fake_redis` | In-memory Redis mock — STM tests without Docker. |
| `decision_ctx` | Factory DecisionContext cho agent unit tests. |
| `platform_config` | load_platform_config(platform-supermarket.yaml). |
| `schema_catalog` | SchemaCatalog.from_dictionary_dir() full. |
| `mini_schema_catalog` | Minimal 1-table catalog. |
| `sample_parquet` | Temp parquet file cho analyst tests. |
| `pipeline_factory` | SupermarketAnalysisPipeline builder với inject mocks. |
| `workflow_state` | new_workflow + start_analysis. |
| `hq_permissions` | build_permissions_snapshot('hq_analyst'). |
| `store_manager_permissions` | build_permissions_snapshot('store_manager', store_ids=[1,2]). |
| `fake_mongo_collection` | InMemoryCollection cho feedback tests. |
| `feedback_loop` | FeedbackLoop với fake Mongo. |

### §W.1.6 — Helpers (`src/project_test/helpers/`)

- **`scripted_invoker.py`:** AgentInvoker trả canned responses theo script.
- **`stub_sql.py`:** SqlGatewayClient mock — validate/execute without DB.
- **`llm_stub.py`:** Bypass LLM calls khi ALLOW_LLM_STUB=1.
- **`fake_mongo.py`:** InMemoryCollection mimicking pymongo.

### §W.1.7 — Lệnh chạy test

```bash
# Toàn bộ suite (stub mode)
uv run pytest packages/project-test -v
# Chỉ unit
uv run pytest packages/project-test/unit -v
# Integration (cần services hoặc mocks)
uv run pytest packages/project-test/integration -v -m 'not live'
# Live SQL/LLM (optional)
uv run pytest packages/project-test/integration/test_live_sql.py -v
```

