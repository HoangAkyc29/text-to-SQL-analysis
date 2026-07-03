# syntax=docker/dockerfile:1
# Extends shared agent-base; installs only chat-gateway package deps on top.
ARG BASE_IMAGE=abstract-base/agent-base:local
ARG UV_PACKAGE=chat-gateway
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
ENV CHAT_GATEWAY_PORT=8300
EXPOSE 8300
CMD ["uv", "run", "chat-gateway"]
