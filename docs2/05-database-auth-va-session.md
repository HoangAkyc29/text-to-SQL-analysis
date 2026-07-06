# Cơ sở dữ liệu, Redis, MongoDB, RBAC

Tách từ [`docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md`](../docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md) (dòng 459–506).

← [Mục lục docs2](README.md)

---

# Phần K — Cơ sở dữ liệu

## §K.1 AUTH DB (supermarket_auth)

Bảng users, roles, user_roles, role_permissions, user_permissions (grant/revoke).

003_password_login.sql — cột password_hash bcrypt.

004_permissions.sql — capability seeds.

## §K.2 Analytics DB1/db2

Readonly user analysisagentreadonly. Tables theo data_dictionary — STRANS shards, SKU_DEF, CUSTOMER, WebRpt_*, v.v.

## §K.3 MongoDB

Database supermarket_agent — collections cho schema docs embedding, analysis_tools promoted recipes.

## §K.4 Redis

Session bundle JSON — workflow state, transcript, clarification pending.

---

# Phần L — Redis và Mongo chi tiết vận hành

Redis key pattern do RedisSessionStore quản lý — load_session(session_id), save_workflow, save_clarification.

Mongo connect timeout MONGODB_CONNECT_TIMEOUT_MS trong orchestrator.

sql-planner dùng mongo_factory.try_create_hybrid_retriever cho schema chunks khi MONGODB_URI reachable.

---

# Phần M — RBAC flow

Login → bcrypt verify auth_store → JWT encode role + store_ids.

Mỗi /chat → load_effective_permissions(user_id) → PermissionsSnapshot.

Pipeline đóng băng permissions trên workflow.

context_policy.can_invoke_tool(agent, tool_name) kiểm tra trước mỗi sandbox/sql tool.

grant_denial helper — default deny nếu capability không match wildcard.

---

