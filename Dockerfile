FROM python:3.10-slim

WORKDIR /app
ENV PYTHONPATH=/app
ENV DB_URL=postgresql+asyncpg://postgres:postgres@db:5432/postgres

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["bash", "-c", "alembic upgrade head && python bot/app.py"]
