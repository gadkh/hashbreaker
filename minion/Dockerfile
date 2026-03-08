FROM python:3.9-slim

WORKDIR /app

COPY minion/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY minion/ ./minion/

ENV PYTHONPATH=/app

CMD ["python", "-m", "minion.main"]