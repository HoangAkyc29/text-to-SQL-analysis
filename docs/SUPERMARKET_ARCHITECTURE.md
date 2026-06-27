# Supermarket Multi-Agent Architecture

Production stack for supermarket analytics chatbot.

## Services

| Service | Port |
|---------|------|
| chat-gateway | 8300 |
| conversational-router (I) | 8201 |
| sql-planner (II) | 8202 |
| risk-reviewer (III) | 8203 |
| data-analyst (IV) | 8204 |
| sql-gateway MCP | 8101 |

## Flow

1. User → `POST /chat` (chat-gateway)
2. Agent I ingress → `route=analysis` + best-effort brief
3. `SupermarketAnalysisPipeline`: II plan → Policy → III risk → execute → IV analyze
4. II may `clarify` → I `clarification_bridge` → auto-resolve or MCQ
5. `FeedbackLoop.on_pipeline_complete` stages case studies on success

## Dev

```bash
uv sync
set ALLOW_LLM_STUB=1
set ALLOW_DEV_AUTH=1
uv run chat-gateway
```

## Docker

```bash
docker compose up --build
```
