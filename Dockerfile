FROM python:3.12-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user requests pytz

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

RUN groupadd -r discordbot && useradd -r -g discordbot discordbot

RUN mkdir -p /tmp && chown discordbot:discordbot /tmp

USER discordbot

COPY status.py ./

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD python -c "import os; exit(0 if os.path.exists('/tmp/health') else 1)"

CMD ["python", "status.py"]
