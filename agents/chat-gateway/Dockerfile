FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install uv && uv sync --frozen || uv sync
ENV AGENT_HTTP_PORT=8200
CMD ["uv", "run", "chat-gateway"]
