FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install uv && uv sync
ENV AGENT_HTTP_PORT=8203
CMD ["uv", "run", "risk-reviewer"]
