FROM python:3.13.5

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "until python -c \"import socket; s=socket.socket(); s.settimeout(2); s.connect(('db',5432)); s.close()\" 2>/dev/null; do echo 'waiting for db...'; sleep 3; done && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
