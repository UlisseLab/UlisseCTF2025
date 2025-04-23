FROM python:3.12

WORKDIR /app

COPY *.py requirements.txt libackend.so ./

RUN apt install gcc
RUN pip install --no-cache-dir -r requirements.txt

CMD gunicorn --preload -w 4 -b 0.0.0.0:$PORT app:app