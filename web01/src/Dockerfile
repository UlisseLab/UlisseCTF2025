FROM python:3.10-alpine

WORKDIR /app
COPY app .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["gunicorn", "-b", "0.0.0.0:6969", "app:app"]