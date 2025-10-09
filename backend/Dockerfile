FROM python:3.10-slim-buster AS builder

WORKDIR /app
COPY app.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

FROM python:3.10-slim-buster

WORKDIR /app


COPY --from=builder /usr/local /usr/local/
COPY --from=builder /app/app.py /app/app.py

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

