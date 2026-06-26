# syntax=docker/dockerfile:1
# Template MCP server — extends abstract-base/mcp-base
ARG BASE_IMAGE=abstract-base/mcp-base:local
ARG UV_PACKAGE=base-mcp-server
FROM ${BASE_IMAGE}
ARG UV_PACKAGE
WORKDIR /app
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package ${UV_PACKAGE} --no-dev
ENV UV_NO_DEV=1
ENV UV_NO_SYNC=1
ENV MCP_TRANSPORT=sse
ENV MCP_HTTP_HOST=0.0.0.0
ENV MCP_HTTP_PORT=8100
ENV AGENT_DATA_DIR=/app/data
EXPOSE 8100
CMD ["uv", "run", "base-mcp-server"]
