FROM python:3.9-slim

WORKDIR /app

COPY master/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY master/ ./master/

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "master.main:app", "--host", "0.0.0.0", "--port", "8000"]