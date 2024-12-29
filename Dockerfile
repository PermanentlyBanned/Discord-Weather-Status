FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir requests pytz

COPY status.py ./

CMD ["python", "status.py"]
