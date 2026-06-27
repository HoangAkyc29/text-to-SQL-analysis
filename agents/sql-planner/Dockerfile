FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install uv && uv sync
ENV AGENT_HTTP_PORT=8202
CMD ["uv", "run", "sql-planner"]
