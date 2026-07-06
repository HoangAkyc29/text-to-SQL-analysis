## §AP.3 — libs/mcp-core + commons

> **Phạm vi:** MCP protocol layer (items 37–50) và shared utilities `libs/commons`. MCP = JSON-RPC cho tools/resources/prompts qua stdio hoặc HTTP/SSE.

### §AP.3.1 — libs/commons

| File | Exports | Mô tả |
|------|---------|-------|
| `libs/commons/src/commons/errors.py` | CommonsError, ConfigError | Hierarchy exception; ConfigError code=config_error |
| `libs/commons/src/commons/logging.py` | get_logger | LOG_LEVEL env; format structured stderr |
| `libs/commons/src/commons/settings.py` | BaseAppSettings | pydantic-settings + .env loading |
| `libs/commons/src/commons/types.py` | Result, JSONValue | Generic Result ok/err; JSON type alias |
| `libs/commons/src/commons/__init__.py` | — | Package marker |

**Sử dụng trong monorepo:**
- Mọi service/agent gọi `commons.logging.get_logger(__name__)`.
- Config loader raise `commons.errors.ConfigError` — catch thống nhất.
- Agent settings subclass `BaseAppSettings` cho env-driven config.
- `Result[T,E]` dùng khi hot path tránh exception (optional).
### §AP.3.2 — mcp-core server layer

| Module | Class | Vai trò |
|--------|-------|---------|
| `mcp_core/server/lifecycle/fastmcp_server.py` | `FastMCPServer` | FastMCP lifecycle wrapper |
| `mcp_core/server/lifecycle/base.py` | `ServerLifecycle` | Start/stop hooks |
| `mcp_core/server/transport/base.py` | `Transport` | stdio / streamable-http / SSE abstraction |
| `mcp_core/server/session/base.py` | `SessionManager` | MCP session state |
| `mcp_core/server/auth/base.py` | `AuthProvider` | Bearer/JWT/composite |
| `mcp_core/server/auth/middleware.py` | `auth_middleware` | Request auth gate |
| `mcp_core/server/auth/factory.py` | `build_auth` | Auth from spec |
| `mcp_core/server/providers/tools/base.py` | `ToolProvider` | Register + invoke tools |
| `mcp_core/server/providers/resources/base.py` | `ResourceProvider` | MCP resources → retrieval |
| `mcp_core/server/providers/prompts/base.py` | `PromptProvider` | MCP prompts → templates |
| `mcp_core/server/capabilities/base.py` | `CapabilityNegotiation` | Protocol handshake |
| `mcp_core/server/callbacks/base.py` | `CallbackHandler` | Progress/logging callbacks |
| `mcp_core/server/notifications/base.py` | `NotificationService` | Server push notifications |
| `mcp_core/server/errors/base.py` | `MCPError` | Structured MCP errors |

### §AP.3.3 — mcp-core client layer

| Module | Class | Vai trò |
|--------|-------|---------|
| `mcp_core/client/connector/base.py` | `MCPConnector, ServerEndpoint` | Connect + discover remote tools |
| `mcp_core/client/connector/strands_connector.py` | `StrandsMCPConnector` | Strands-specific transport |
| `mcp_core/client/registry/base.py` | `MCPServerRegistry` | Multi-server registry + prefixes |
| `mcp_core/client/registry/strands_registry.py` | `StrandsMCPServerRegistry` | Used by BaseAgentService |
| `mcp_core/client/registry/tool_filter.py` | `ToolFilter` | Allow/deny tool names |
| `mcp_core/client/adapter/base.py` | `MCPAgentAdapter` | MCP tool → agent tool handle |
| `mcp_core/client/adapter/strands_adapter.py` | `StrandsMCPAgentAdapter` | → Strands Agent tools |

### §AP.3.4 — Luồng MCP JSON-RPC

```
Agent (Strands)                    MCP Server (sql-gateway)
     |                                      |
     |--- initialize ----------------------->|
     |<-- capabilities ----------------------|
     |--- tools/list ----------------------->|
     |<-- [{name, inputSchema}] -------------|
     |--- tools/call {name, arguments} ----->|
     |<-- {content:[{type:text}], isError} --|
```
**Mapping sang agent-core (README mcp-core):**
- MCP tool → `capabilities.tools.AbstractTool`
- MCP resource → `capabilities.retrieval` / memory
- MCP prompt → `capabilities.prompts.PromptTemplate`
### §AP.3.5 — Wiring supermarket

| Server | Transport | Prefix | Thực thi bởi |
|--------|-----------|--------|--------------|
| sql-gateway | SSE (`SQL_GATEWAY_URL`) | `sql` | Pipeline `HttpSqlGatewayClient`, không agent ReAct |
| python-sandbox | stdio (`uv run python-sandbox`) | `sandbox` | Pipeline process, không agent ReAct |
Comment trong `platform-supermarket.yaml`: tool ownership thuộc pipeline/gateway — agents trả JSON; chat-gateway + SupermarketAnalysisPipeline gọi MCP.
### §AP.3.6 — Adapter chain (tool → LLM)

1. `PlatformMCPRegistry.endpoints_for(['sql-gateway'])` → `ServerEndpoint`.
2. `StrandsMCPServerRegistry.add(endpoint)` + context manager connect.
3. `registry.adapted_tools(StrandsMCPAgentAdapter)` → list Strands-compatible tools.
4. `StrandsAgent(model, tools=...)` — LLM nhận tool specs trong API call.
5. LLM emit tool_call → adapter → MCP `tools/call` → result text → next turn.
**ToolFilter:** `MCPServerSpec.tool_filters` giới hạn expose subset tools per server.
### §AP.3.7 — Inventory file mcp-core

| File | Docstring |
|------|-----------|
| `libs/mcp-core/src/mcp_core/__init__.py` | mcp-core: abstract building blocks for MCP servers and clients (items 37-50). |
| `libs/mcp-core/src/mcp_core/client/__init__.py` | G (client side): connector, multi-server registry, MCP<->Agent adapter |
| `libs/mcp-core/src/mcp_core/client/adapter/__init__.py` | Item 50 - MCP <-> Agent adapter (bridge). |
| `libs/mcp-core/src/mcp_core/client/adapter/base.py` | Item 50 - MCP <-> Agent adapter (bridge). |
| `libs/mcp-core/src/mcp_core/client/adapter/strands_adapter.py` | Strands implementation of the MCP <-> Agent adapter. |
| `libs/mcp-core/src/mcp_core/client/connector/__init__.py` | Item 48 - MCP Client / Connector. |
| `libs/mcp-core/src/mcp_core/client/connector/base.py` | Item 48 - MCP Client / Connector. |
| `libs/mcp-core/src/mcp_core/client/connector/strands_connector.py` | Strands-backed reference implementation of :class:`MCPConnector`. |
| `libs/mcp-core/src/mcp_core/client/registry/__init__.py` | Item 49 - MCP server registry / Multi-server manager. |
| `libs/mcp-core/src/mcp_core/client/registry/base.py` | Item 49 - MCP server registry / Multi-server manager. |
| `libs/mcp-core/src/mcp_core/client/registry/strands_registry.py` | Strands-backed multi-server registry: builds StrandsMCPConnector per endpoint. |
| `libs/mcp-core/src/mcp_core/client/registry/tool_filter.py` | Tool name filtering for MCP server endpoints. |
| `libs/mcp-core/src/mcp_core/server/__init__.py` | G (server side): MCP server lifecycle, transport, capabilities, providers, |
| `libs/mcp-core/src/mcp_core/server/auth/__init__.py` | Item 45 - Auth / Authorization. |
| `libs/mcp-core/src/mcp_core/server/auth/base.py` | MCP server authentication and authorization. |
| `libs/mcp-core/src/mcp_core/server/auth/factory.py` | Build MCP authorizers from config. |
| `libs/mcp-core/src/mcp_core/server/auth/middleware.py` | Auth middleware wrapping MCP tool handlers. |
| `libs/mcp-core/src/mcp_core/server/callbacks/__init__.py` | Item 43 - Client-callback handler (server calls back to client). |
| `libs/mcp-core/src/mcp_core/server/callbacks/base.py` | Item 43 - Client-callback handler (server -> client). |
| `libs/mcp-core/src/mcp_core/server/capabilities/__init__.py` | Item 39 - Capability negotiation. |
| `libs/mcp-core/src/mcp_core/server/capabilities/base.py` | Item 39 - Capability negotiation. |
| `libs/mcp-core/src/mcp_core/server/errors/__init__.py` | Item 47 - Error handling (domain -> JSON-RPC). |
| `libs/mcp-core/src/mcp_core/server/errors/base.py` | Item 47 - Error handling. |
| `libs/mcp-core/src/mcp_core/server/lifecycle/__init__.py` | Item 37 - MCP Server (base / lifecycle). |
| `libs/mcp-core/src/mcp_core/server/lifecycle/base.py` | Item 37 - MCP Server (base / lifecycle). |
| `libs/mcp-core/src/mcp_core/server/lifecycle/fastmcp_server.py` | FastMCP-backed reference implementation of :class:`AbstractMCPServer`. |
| `libs/mcp-core/src/mcp_core/server/notifications/__init__.py` | Item 46 - Notifications / Progress / Cancellation. |
| `libs/mcp-core/src/mcp_core/server/notifications/base.py` | Item 46 - Notifications / Progress / Cancellation. |
| `libs/mcp-core/src/mcp_core/server/providers/__init__.py` | MCP primitives exposed by a server: tools (40), resources (41), prompts (42). |
| `libs/mcp-core/src/mcp_core/server/providers/prompts/__init__.py` | Item 42 - Prompt provider (primitive: template). |
| `libs/mcp-core/src/mcp_core/server/providers/prompts/base.py` | Item 42 - Prompt provider (primitive: template). |
| `libs/mcp-core/src/mcp_core/server/providers/resources/__init__.py` | Item 41 - Resource provider (primitive: read-only data). |
| `libs/mcp-core/src/mcp_core/server/providers/resources/base.py` | Item 41 - Resource provider (primitive: read-only data). |
| `libs/mcp-core/src/mcp_core/server/providers/tools/__init__.py` | Item 40 - Tool provider (primitive: action, has side-effects). |
| `libs/mcp-core/src/mcp_core/server/providers/tools/base.py` | Item 40 - Tool provider (primitive: action). |
| `libs/mcp-core/src/mcp_core/server/session/__init__.py` | Item 44 - Session / Connection. |
| `libs/mcp-core/src/mcp_core/server/session/base.py` | Item 44 - Session / Connection. |
| `libs/mcp-core/src/mcp_core/server/transport/__init__.py` | Item 38 - Transport (stdio / streamable-http). |
| `libs/mcp-core/src/mcp_core/server/transport/base.py` | Item 38 - Transport. |


