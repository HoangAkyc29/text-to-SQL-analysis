# Auth SQL Server — supermarket_auth

Database **chỉ** cho đăng nhập user (username/password). Không dùng cho query kinh doanh.

## Khởi tạo nhanh (1 lệnh)

Cần login admin SQL Server (sysadmin/dbcreator) — login analytics read-only KHÔNG đủ:

```powershell
$env:AUTH_DB_ADMIN_USER="sa"             # tùy chọn, mặc định lấy Uid trong AUTH_DB_DSN
$env:AUTH_DB_ADMIN_PASSWORD="<sa pw thật>"
uv run python scripts/init_auth_db.py
```

Script tạo DB `supermarket_auth` → chạy `001` → `003` → `004` → seed user
(`scripts/seed_auth.py`), idempotent. Server lấy từ `AUTH_DB_DSN`
(`host.docker.internal` được đổi thành `localhost` khi chạy trên host; override bằng
`AUTH_DB_INIT_SERVER`).

## Thứ tự chạy migration (thủ công)

```sql
-- 1. Schema (fresh install)
001_schema.sql

-- 2. Nếu DB đã có từ bản cũ (chưa có username/password_hash)
003_password_login.sql

-- 3. RBAC capability: permissions / roles / role_permissions / user_permissions
--    + seed role admin, hq_analyst, store_manager (mirror config/project.yaml)
004_permissions.sql
```

Sau khi chạy SQL, **seed user bằng script** (hash + salt lúc runtime — KHÔNG commit
hash/password vào repo):

```powershell
# Password riêng cho từng user qua env (khuyến nghị), nếu không set sẽ dùng
# default bootstrap và script cảnh báo rotate:
$env:AUTH_SEED_ADMIN_PASSWORD="..."
$env:AUTH_SEED_HQ_ANALYST_PASSWORD="..."
$env:AUTH_SEED_STORE_MANAGER_PASSWORD="..."
uv run python scripts/seed_auth.py
```

Script upsert 3 user (`admin`, `hq.analyst`, `store.manager`) với `user_id` GUID cố
định, idempotent, không đụng các row khác.

## Phân quyền (capability RBAC)

Quyền được resolve theo user từ AUTH DB:

- `role_permissions[user.role]` UNION `user_permissions(effect='grant')` MINUS `user_permissions(effect='revoke')`.
- Capability key: `data:table:<NAME>` / `data:column_deny:<COL>` / `data:store_filter:required` / `tool:<server>:<action>` / `function:<tool_id>`. Wildcard: `tool:*`, `data:table:*`, `function:*`.
- Role `admin` = full quyền (`data:table:*`, `tool:*`, `function:*`).

Chi tiết: [`docs/AUTH_AND_PERMISSIONS.md`](../../../docs/AUTH_AND_PERMISSIONS.md).

### Cấp/thu quyền riêng cho 1 user

```sql
-- Thu quyền chạy 1 tool của user cụ thể (override role)
INSERT INTO user_permissions (user_id, permission_key, effect)
VALUES ('<user-guid>', 'tool:python-sandbox:export_excel', 'revoke');

-- Cấp thêm quyền 1 bảng
INSERT INTO user_permissions (user_id, permission_key, effect)
VALUES ('<user-guid>', 'data:table:ACCOUNT', 'grant');
```

## Connection

`.env` → `AUTH_DB_DSN` (host port mặc định local: **18435** — xem [`docs/PORTS.md`](../../../docs/PORTS.md)).

## Tạo user mới

```powershell
uv run python scripts/hash_password.py "YourPassword"
```

```sql
INSERT INTO users (username, email, display_name, role, store_ids, password_hash, is_active)
VALUES (
  'new.user',
  'user@company.local',
  'Display Name',
  'store_manager',
  '10001',
  '<bcrypt-hash>',
  1
);
```

## Code

- Login: `POST /auth/login` — [`agents/chat-gateway/src/chat_gateway/auth_store.py`](../../../agents/chat-gateway/src/chat_gateway/auth_store.py)
- Docs: [`docs/AUTH_AND_PERMISSIONS.md`](../../../docs/AUTH_AND_PERMISSIONS.md)
