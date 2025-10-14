FROM python:3.10-bookworm

# Install the PostgreSQL client runtime library.
# 'libpq5' is the minimal library needed for psycopg2 to connect to Postgres,
# avoiding the larger development libraries (like libpq-dev and gcc).
#
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt psycopg2-binary gunicorn

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

