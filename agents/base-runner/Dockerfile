# syntax=docker/dockerfile:1
# Template runner — extends abstract-base/agent-base, profile: runner
ARG BASE_IMAGE=abstract-base/agent-base:local
ARG UV_PACKAGE=base-runner
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
ENV PLATFORM_TRANSPORT=http
ENV BASE_AGENT_URL=http://base-agent:8200
CMD ["uv", "run", "base-runner", "--once", "--no-llm"]
