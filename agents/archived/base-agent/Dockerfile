# syntax=docker/dockerfile:1
# Template agent service — extends abstract-base/agent-base
# TODO: copy and set UV_PACKAGE when creating a new agent image
ARG BASE_IMAGE=abstract-base/agent-base:local
ARG UV_PACKAGE=base-agent
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
ENV AGENT_HTTP_HOST=0.0.0.0
ENV AGENT_HTTP_PORT=8200
EXPOSE 8200
CMD ["uv", "run", "base-agent"]
