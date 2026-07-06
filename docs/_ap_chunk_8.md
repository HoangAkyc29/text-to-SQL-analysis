## §Y.1 — Mọi script trong scripts/

> **Phạm vi:** Operational và dev scripts tại `scripts/` — không bao gồm generator tạm `_gen_*` nội bộ trừ khi ghi chú.

### §Y.1.1 — Bảng tổng hợp

| Script | Nhóm | Mô tả | Lệnh |
|--------|------|-------|------|
| `init_auth_db.py` | DB init | Schema + RBAC + seed users trên AUTH DB | `uv run python scripts/init_auth_db.py` |
| `seed_auth.py` | Auth | Upsert 3 users bcrypt — env AUTH_SEED_*_PASSWORD | `uv run python scripts/seed_auth.py` |
| `hash_password.py` | Auth util | Hash password one-off cho manual seed | `uv run python scripts/hash_password.py 'secret'` |
| `gen_rbac_seed.py` | Auth codegen | Generate RBAC seed SQL/data | `uv run python scripts/gen_rbac_seed.py` |
| `index_schema_docs.py` | Docs | Index data_dictionary → search docs | `uv run python scripts/index_schema_docs.py` |
| `generate_data_dictionary.py` | Schema | Generate data_dictionary YAML từ DB | `uv run python scripts/generate_data_dictionary.py` |
| `validate_data_dictionary.py` | Schema QA | Validate dictionary structure/consistency | `uv run python scripts/validate_data_dictionary.py` |
| `validate_tcvn3_samples.py` | Encoding | Validate TCVN3 sample files | `uv run python scripts/validate_tcvn3_samples.py` |
| `explore_db_samples.py` | DB explore | Export TOP-N row samples từ analytics DB | `uv run python scripts/explore_db_samples.py` |
| `explore_db_deep.py` | DB explore | Deep column stats + semantics hints | `uv run python scripts/explore_db_deep.py` |
| `audit_semantics.py` | DB QA | Audit dictionary semantics vs TOP-20 samples | `uv run python scripts/audit_semantics.py` |
| `semantic_evidence.py` | DB QA | Collect semantic evidence for columns | `uv run python scripts/semantic_evidence.py` |
| `cleanup_artifacts.py` | Ops | TTL cleanup data/artifacts per project.yaml | `uv run python scripts/cleanup_artifacts.py` |
| `docker-build.ps1` | Deploy | PowerShell multi-image Docker build | `./scripts/docker-build.ps1` |
| `gen_z3_append.py` | Docs gen | Generate §Z.3 pipeline line-by-line appendix | `uv run python scripts/gen_z3_append.py` |
| `gen_ah1_contracts_append.py` | Docs gen | Generate §AH.1 Pydantic contracts appendix | `uv run python scripts/gen_ah1_contracts_append.py` |
| `_gen_j1_append.py` | Docs gen | Generate §J.1 env var appendix (internal) | `uv run python scripts/_gen_j1_append.py` |
| `gen_ap_append.py` | Docs gen | Generate §AP/I/W/Y appendix (this script) | `uv run python scripts/gen_ap_append.py` |

### §Y.1.2 — `init_auth_db.py`

**Nhóm:** DB init
**Mô tả:** Schema + RBAC + seed users trên AUTH DB
**Lệnh:** `uv run python scripts/init_auth_db.py`

**Docstring:** Initialize AUTH DB contents: schema + capability RBAC + seed users.

**Functions:**
- `parse_dsn()`
- `run_file()`
- `main()`

**Khi nào chạy:**
- Lần đầu setup AUTH DB; sau migrate SQL auth/*.sql.

**Phụ thuộc env:**
- AUTH_DB_DSN, AUTH_DB_INIT_SERVER (optional)

### §Y.1.3 — `seed_auth.py`

**Nhóm:** Auth
**Mô tả:** Upsert 3 users bcrypt — env AUTH_SEED_*_PASSWORD
**Lệnh:** `uv run python scripts/seed_auth.py`

**Docstring:** Seed AUTH DB users. Passwords are hashed + salted at runtime (bcrypt).

**Functions:**
- `main()`

**Khi nào chạy:**
- Sau init_auth_db; rotate password qua env.

**Phụ thuộc env:**
- AUTH_DB_DSN, AUTH_SEED_ADMIN_PASSWORD, AUTH_SEED_HQ_ANALYST_PASSWORD, AUTH_SEED_STORE_MANAGER_PASSWORD

### §Y.1.4 — `hash_password.py`

**Nhóm:** Auth util
**Mô tả:** Hash password one-off cho manual seed
**Lệnh:** `uv run python scripts/hash_password.py 'secret'`

**Docstring:** Print bcrypt hash for AUTH DB seed / user setup.

**Functions:**
- `main()`

**Khi nào chạy:**
- Theo nhu cầu dev/ops.

**Phụ thuộc env:**
- Xem docstring script.

### §Y.1.5 — `gen_rbac_seed.py`

**Nhóm:** Auth codegen
**Mô tả:** Generate RBAC seed SQL/data
**Lệnh:** `uv run python scripts/gen_rbac_seed.py`

**Docstring:** Generate deploy/sql/auth/004_permissions.sql from a single source of truth.

**Functions:**
- `render()`
- `main()`

**Khi nào chạy:**
- Theo nhu cầu dev/ops.

**Phụ thuộc env:**
- Xem docstring script.

### §Y.1.6 — `index_schema_docs.py`

**Nhóm:** Docs
**Mô tả:** Index data_dictionary → search docs
**Lệnh:** `uv run python scripts/index_schema_docs.py`

**Docstring:** Index schema markdown files into Mongo vector collections.

**Functions:**
- `main()`

**Khi nào chạy:**
- Theo nhu cầu dev/ops.

**Phụ thuộc env:**
- Xem docstring script.

### §Y.1.7 — `generate_data_dictionary.py`

**Nhóm:** Schema
**Mô tả:** Generate data_dictionary YAML từ DB
**Lệnh:** `uv run python scripts/generate_data_dictionary.py`

**Docstring:** Generate data_dictionary/tables/db1|db2/*.md from JSON schema exports + exploration report.

**Functions:**
- `db1_table_meta()`
- `db2_table_meta()`
- `describe_column()`
- `load_json_tables()`
- `pick_schema()`
- `yaml_scalar()`
- `render_table_md()`
- `main()`

**Khi nào chạy:**
- Theo nhu cầu dev/ops.

**Phụ thuộc env:**
- Xem docstring script.

### §Y.1.8 — `validate_data_dictionary.py`

**Nhóm:** Schema QA
**Mô tả:** Validate dictionary structure/consistency
**Lệnh:** `uv run python scripts/validate_data_dictionary.py`

**Docstring:** Validate data_dictionary against live db1/db2 (read-only).

**Functions:**
- `connect()`
- `list_user_tables()`
- `table_columns()`
- `min_max_date()`
- `cutoff_date()`
- `parse_md_columns()`
- `load_json_tables()`
- `main()`

**Khi nào chạy:**
- Theo nhu cầu dev/ops.

**Phụ thuộc env:**
- Xem docstring script.

### §Y.1.9 — `validate_tcvn3_samples.py`

**Nhóm:** Encoding
**Mô tả:** Validate TCVN3 sample files
**Lệnh:** `uv run python scripts/validate_tcvn3_samples.py`

**Docstring:** Validate tcvn3_to_unicode against tests/sample_tcvn3/sampletcvn3.txt.

**Functions:**
- `main()`

**Khi nào chạy:**
- Theo nhu cầu dev/ops.

**Phụ thuộc env:**
- Xem docstring script.

### §Y.1.10 — `explore_db_samples.py`

**Nhóm:** DB explore
**Mô tả:** Export TOP-N row samples từ analytics DB
**Lệnh:** `uv run python scripts/explore_db_samples.py`

**Docstring:** Read-only sample explorer — tables from JSON exports only, TOP 20 per table.

**Functions:**
- `load_table_names()`
- `connect()`
- `sample_table()`
- `summarize_key_columns()`
- `explore_db()`
- `main()`

**Khi nào chạy:**
- Theo nhu cầu dev/ops.

**Phụ thuộc env:**
- ANALYTICS_DB_DSN

### §Y.1.11 — `explore_db_deep.py`

**Nhóm:** DB explore
**Mô tả:** Deep column stats + semantics hints
**Lệnh:** `uv run python scripts/explore_db_deep.py`

**Docstring:** Deep read-only DB exploration (TOP 20 / table) — raw stats to db_exploration_samples/.

**Functions:**
- `load_schema()`
- `connect()`
- `cell_str()`
- `is_text_column()`
- `sample_table()`
- `analyze_table()`
- `global_aggregates()`
- `logical_group()`
- `render_report()`
- `explore_db()`

**Khi nào chạy:**
- Theo nhu cầu dev/ops.

**Phụ thuộc env:**
- Xem docstring script.

### §Y.1.12 — `audit_semantics.py`

**Nhóm:** DB QA
**Mô tả:** Audit dictionary semantics vs TOP-20 samples
**Lệnh:** `uv run python scripts/audit_semantics.py`

**Docstring:** Audit table/column semantics in data_dictionary against TOP-20 samples.

**Functions:**
- `load_samples()`
- `parse_md()`
- `col_values()`
- `is_generic()`
- `check_mark_amount_ratio()`
- `audit_table()`
- `main()`

**Khi nào chạy:**
- Sau update data_dictionary hoặc DB schema change.

**Phụ thuộc env:**
- Xem docstring script.

### §Y.1.13 — `semantic_evidence.py`

**Nhóm:** DB QA
**Mô tả:** Collect semantic evidence for columns
**Lệnh:** `uv run python scripts/semantic_evidence.py`

**Docstring:** Extract semantic evidence from TOP-20 samples for manual review.

**Functions:**
- `parse_md()`
- `profile_table()`
- `main()`

**Khi nào chạy:**
- Theo nhu cầu dev/ops.

**Phụ thuộc env:**
- Xem docstring script.

### §Y.1.14 — `cleanup_artifacts.py`

**Nhóm:** Ops
**Mô tả:** TTL cleanup data/artifacts per project.yaml
**Lệnh:** `uv run python scripts/cleanup_artifacts.py`

**Docstring:** Remove artifact traces older than configured TTL.

**Functions:**
- `cleanup()`
- `main()`

**Khi nào chạy:**
- Cron hàng ngày; trước khi disk full.

**Phụ thuộc env:**
- Đọc config/project.yaml artifacts.*

### §Y.1.15 — `docker-build.ps1`

**Nhóm:** Deploy
**Mô tả:** PowerShell multi-image Docker build
**Lệnh:** `./scripts/docker-build.ps1`

**Khi nào chạy:**
- CI/CD build images trước deploy.

**Phụ thuộc env:**
- Xem docstring script.

### §Y.1.16 — `gen_z3_append.py`

**Nhóm:** Docs gen
**Mô tả:** Generate §Z.3 pipeline line-by-line appendix
**Lệnh:** `uv run python scripts/gen_z3_append.py`

**Docstring:** Generate Z.3 appendix for TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md

**Functions:**
- `add_subsection()`

**Khi nào chạy:**
- Theo nhu cầu dev/ops.

**Phụ thuộc env:**
- Xem docstring script.

### §Y.1.17 — `gen_ah1_contracts_append.py`

**Nhóm:** Docs gen
**Mô tả:** Generate §AH.1 Pydantic contracts appendix
**Lệnh:** `uv run python scripts/gen_ah1_contracts_append.py`

**Docstring:** Generate §AH.1 Pydantic contracts appendix for TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md.

**Functions:**
- `set_field()`
- `set_class()`
- `extract_models_from_file()`
- `json_example_for()`
- `validation_notes()`
- `producer_consumer_field()`
- `field_detail_block()`
- `json_fragment()`
- `enum_section()`
- `model_section()`

**Khi nào chạy:**
- Theo nhu cầu dev/ops.

**Phụ thuộc env:**
- Xem docstring script.

### §Y.1.18 — `_gen_j1_append.py`

**Nhóm:** Docs gen
**Mô tả:** Generate §J.1 env var appendix (internal)
**Lệnh:** `uv run python scripts/_gen_j1_append.py`

**Docstring:** One-off generator for §J.1 env var appendix. Run then delete.

**Functions:**
- `env_section()`
- `main()`

**Khi nào chạy:**
- Theo nhu cầu dev/ops.

**Phụ thuộc env:**
- Xem docstring script.

### §Y.1.19 — `gen_ap_append.py`

**Nhóm:** Docs gen
**Mô tả:** Generate §AP/I/W/Y appendix (this script)
**Lệnh:** `uv run python scripts/gen_ap_append.py`

**Docstring:** Generate AP/I/W/Y appendix sections for TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md.

**Functions:**
- `section_ap1()`
- `section_ap2()`
- `section_ap3()`
- `section_i1_detail()`
- `section_i2_detail()`
- `section_i3_detail()`
- `section_w1()`
- `section_y1()`
- `main()`

**Khi nào chạy:**
- Regenerate doc appendix sau thay đổi libs/config/tests.

**Phụ thuộc env:**
- Xem docstring script.

