FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install uv && uv sync
EXPOSE 8101
CMD ["uv", "run", "sql-gateway"]
