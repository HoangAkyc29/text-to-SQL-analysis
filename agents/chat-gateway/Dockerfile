# syntax=docker/dockerfile:1
# Extends shared agent-base; installs only chat-gateway package deps on top.
ARG BASE_IMAGE=abstract-base/agent-base:local
ARG UV_PACKAGE=chat-gateway
FROM ${BASE_IMAGE}
ARG UV_PACKAGE

# Microsoft ODBC Driver 18 for AUTH DB login (pyodbc in auth_store)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl gnupg ca-certificates \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
        | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
        > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 unixodbc \
    && rm -rf /var/lib/apt/lists/*

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
