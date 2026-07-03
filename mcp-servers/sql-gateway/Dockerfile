# syntax=docker/dockerfile:1
# Extends shared mcp-base; HTTP entrypoint for pipeline HttpSqlGatewayClient.
ARG BASE_IMAGE=abstract-base/mcp-base:local
ARG UV_PACKAGE=sql-gateway
FROM ${BASE_IMAGE}
ARG UV_PACKAGE
WORKDIR /app
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package ${UV_PACKAGE} --no-dev
ENV UV_NO_DEV=1
ENV UV_NO_SYNC=1
ENV AGENT_ROOT_DIR=/app
ENV AGENT_DATA_DIR=/app/data
ENV SQL_GATEWAY_HTTP_PORT=8101
EXPOSE 8101
CMD ["uv", "run", "sql-gateway-http"]
