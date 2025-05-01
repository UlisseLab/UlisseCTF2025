FROM python:3.10-slim@sha256:06f6d69d229bb55fab83dded514e54eede977e33e92d855ba3f97ce0e3234abc

WORKDIR /app
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7788

CMD ["python", "app.py"]
