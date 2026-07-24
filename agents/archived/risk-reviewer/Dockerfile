# syntax=docker/dockerfile:1
ARG BASE_IMAGE=abstract-base/agent-base:local
ARG UV_PACKAGE=risk-reviewer
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
ENV AGENT_HTTP_PORT=8203
EXPOSE 8203
CMD ["uv", "run", "risk-reviewer"]
