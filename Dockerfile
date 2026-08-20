FROM python:3.12.14 AS builder
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
RUN python -m venv .venv
COPY requirements.txt ./
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.12.14-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .
ENV PORT=8080
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8080
CMD ["/app/.venv/bin/python", "main.py"]
