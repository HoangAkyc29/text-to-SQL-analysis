# mcp-core

Shared, abstract building blocks for MCP **servers** and **clients** (items 37-50).
Built on the official `mcp` SDK and Strands' MCP integration.

- `server/` - lifecycle, transport, capability negotiation, tool/resource/prompt
  providers, client-callbacks, sessions, auth, notifications, errors (37-47).
- `client/` - connector, multi-server registry, and the MCP <-> Agent adapter
  that maps MCP primitives onto `agent_core` abstractions (48-50).

The adapter (`client/adapter`) is the key seam: it turns remote MCP tools into
`agent_core` Tools (item 9), resources into Retriever/Memory sources (12/13), and
prompts into PromptTemplates (item 7), so an agent never needs to know a tool is
remote.
