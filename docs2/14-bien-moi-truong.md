# Biến môi trường (khái quát + chi tiết)

Tách từ [`docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md`](../docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md) (dòng 417–458).

← [Mục lục docs2](README.md)

---

# Phần J — Biến môi trường (khái quát)

## §J.1 LLM

OPENROUTER_API_KEY — bắt buộc prod.

ALLOW_LLM_STUB — 0 prod, 1 test keyword/stub SQL.

## §J.2 Infra

REDIS_URL, MONGODB_URI — compose override internal DNS.

## §J.3 Service URLs

AGENT_I_URL … AGENT_IV_URL, SQL_GATEWAY_URL, CHAT_GATEWAY_PORT.

## §J.4 Analytics SQL

ANALYTICS_DB_DSN, ANALYTICS_DB_DSN_2 — ODBC readonly.

AUTH_DB_DSN — supermarket_auth app user.

## §J.5 Auth

JWT_SECRET, REQUIRE_PROD_AUTH, ALLOW_DEV_AUTH.

REQUIRE_INTERNAL_AUTH, INTERNAL_SERVICE_TOKEN.

AUTH_SEED_*_PASSWORD — seed users.

## §J.6 Prod overlay

REDIS_PASSWORD, MONGO_ROOT_USER, MONGO_ROOT_PASSWORD.

PUBLIC_DOMAIN, TLS_EMAIL — Caddy.

## §J.7 Tuning

LOG_LEVEL, AUTH_PERMISSIONS_CACHE_TTL, SANDBOX_MAX_ROWS, SANDBOX_MAX_SECONDS, SQL_GATEWAY_MAX_CONCURRENT, MONGODB_CONNECT_TIMEOUT_MS, SQL_AUDIT_LOG_PATH.

---

