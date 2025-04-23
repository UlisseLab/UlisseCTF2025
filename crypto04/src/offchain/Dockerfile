FROM python@sha256:06f6d69d229bb55fab83dded514e54eede977e33e92d855ba3f97ce0e3234abc

# Install system deps
RUN apt-get update && apt-get install -y curl gcc libffi-dev libssl-dev

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . /app
WORKDIR /app

# Expose Flask port
EXPOSE 5001

# Entrypoint
CMD ["python", "offchain.py"]
