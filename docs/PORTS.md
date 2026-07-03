# Supermarket stack — local port map

Dải **`18xxx`** tránh cổng mặc định (6379, 27017, 8000, 3000, 5432, 1433) và conflict với stack khác trên cùng máy.

| Service | Host (localhost) | Trong Docker network | Ghi chú |
|---------|------------------|----------------------|---------|
| Redis | **18379** | `redis:6379` | Map `18379:6379` |
| MongoDB | **18217** | `mongodb:27017` | Map `18217:27017`; không đụng `mongod` hệ thống :27017 |
| sql-gateway HTTP | **18101** | `sql-gateway:18101` | `SQL_GATEWAY_HTTP_PORT=18101` |
| Agent I | **18201** | `conversational-router:18201` | |
| Agent II | **18202** | `sql-planner:18202` | |
| Agent III | **18203** | `risk-reviewer:18203` | |
| Agent IV | **18204** | `data-analyst:18204` | |
| chat-gateway | **18300** | `chat-gateway:18300` | `POST /auth/login`, `/chat` |
| Auth SQL (tùy chọn) | **18435** | — | `AUTH_DB_DSN` — ODBC từ host |
**`.env` khi chạy trên host** (uv / client gọi localhost):

```dotenv
REDIS_URL=redis://localhost:18379/0
MONGODB_URI=mongodb://localhost:18217/supermarket_agent
SQL_GATEWAY_URL=http://localhost:18101
AGENT_I_URL=http://localhost:18201
AGENT_II_URL=http://localhost:18202
AGENT_III_URL=http://localhost:18203
AGENT_IV_URL=http://localhost:18204
CHAT_GATEWAY_URL=http://localhost:18300
```

**Docker Compose** publish host ports ở trên; `chat-gateway` override URL nội bộ qua tên service (xem `docker-compose.yaml`).

```powershell
docker compose pull redis mongodb
docker compose up -d redis mongodb   # chỉ infra
docker compose up -d                 # full stack
```

Data Redis/Mongo lưu trong volumes `supermarket-redis`, `supermarket-mongo` — không cần cài native trên Windows.
