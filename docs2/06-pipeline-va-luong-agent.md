# Pipeline, Agent I–IV chi tiết luồng

Tách từ [`docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md`](../docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md) (dòng 507–632).

← [Mục lục docs2](README.md)

---

# Phần N — Pipeline từng bước (SupermarketAnalysisPipeline.run)

Bước N.1: Khởi tạo trace_id, out_dir dưới data/artifacts/{trace_id}.

Bước N.2: decompose_brief nếu brief.plan None.

Bước N.3: Vòng sql_attempt 1..max_sql_retries.

Bước N.4: Gọi Agent II với schema_context đã lọc theo allowed_tables.

Bước N.5: Nếu action clarify → return NEEDS_CLARIFICATION (trừ exploration_mode).

Bước N.6: Với mỗi SQL — PolicyEngine.validate local.

Bước N.7: Gọi Agent III review.

Bước N.8: sql_gateway.execute_readonly với SqlAclContext.

Bước N.9: Ghi parquet query_{i}.parquet.

Bước N.10: build_execution_plan + gọi Agent IV.

Bước N.11: Nếu data_feedback → inbox → continue vòng II.

Bước N.12: Nếu complete → FeedbackLoop stage case study.

Bước N.13: AuditLogger log sql events vào SQL_AUDIT_LOG_PATH.

---

# Phần O — Agent I chi tiết modes

### O.1 ingress

Parse message JSON hoặc text. external_sources từ session bundle merge vào brief sau ingress.

LLM trả route + brief. satisfaction_signal từ detect_satisfaction heuristic.

### O.2 clarification_bridge

Merge transcript + clarification_request → answers JSON cho pipeline resume.

### O.3 clarify

Format câu hỏi MCQ cho user từ ClarificationRequest.

### O.4 synthesize

Nhận technical_summary → user_message tiếng Việt + artifact list.

---

# Phần P — Agent II chi tiết

retrieve(brief.intent) — hybrid mongo chunks nếu retriever configured.

apply_data_feedback khi inbox có data_feedback từ IV.

probe_mode khi IV gửi probe_requests.

Output sql_queries list — mỗi query có target_db trong query_meta.

---

# Phần Q — Agent III chi tiết

PolicyEngine local validate trước LLM soft review.

Verdict approve → pipeline execute. reject → risk_feedback → II retry.

needs_explain → attach explain plan từ sql-gateway.

---

# Phần R — Agent IV và iv_analyzer chi tiết

R.1: Merge external parquet với SQL paths.

R.2: Empty / identifier_mismatch → data_feedback.

R.3: Chạy execution_plan steps — run_analysis_script.

R.4: chart nếu output_format chứa chart — plot cột 0 vs 1.

R.5: exploration_mode → suggest_clarify.

R.6: export_excel tool tồn tại nhưng iv_analyzer không gọi.

R.7: max_steps budget — dừng sớm với coverage gaps.

---

# Phần S — sql-gateway

Semaphore SQL_GATEWAY_MAX_CONCURRENT.

Rate limit per actor_id.

TCVN3 maybe_decode_row trên mỗi row execute_readonly.

get_schema_snapshot cần tool_grants.

---

# Phần T — python-sandbox

_guard_output_dir — chỉ ghi dưới ARTIFACTS_DIR.

run_analysis_script — subprocess runner_child, timeout SANDBOX_MAX_SECONDS.

Child env copy full os.environ (lưu ý secrets).

---

# Phần U — chat-gateway orchestrator

handle_chat → Agent I ingress → nếu analysis → pipeline.run.

handle_clarify → apply_clarification_reply → pipeline resume.

attach_external_sources → brief.external_sources append.

_invoke_agent_i inject session_bundle transcript vào metadata.

---

