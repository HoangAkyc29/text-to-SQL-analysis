# mcp-servers/

Deployable MCP server images (tools exposed to agents via MCP).

## Template: `base-mcp-server`

Copy → `my-<domain>-server/` when adding tools:

1. Implement handlers in `tools_impl.py`
2. Register via `providers.py` ToolProvider
3. Update `pyproject.toml` script name
4. Register in `platform.yaml` (`mcp_servers`, prefix, transport)
5. Add to `docker/images.yaml` and compose

Reference: Monorepo-Abstract-Agent-Strands `mcp-servers/crypto-features-server/`
