FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir requests pytz

RUN apt-get remove -y gcc && apt-get autoremove -y

RUN groupadd -r discord && useradd -r -g discord discord

RUN mkdir -p /tmp && chown discord:discord /tmp

USER discordbot

COPY status.py ./

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD python -c "import os; exit(0 if os.path.exists('/tmp/health') else 1)"

CMD ["python", "status.py"]
