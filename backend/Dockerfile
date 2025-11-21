FROM python:3.11-slim

WORKDIR /app

# Install ping dependencies (iputils-ping is often needed for ping command, but ping3 uses raw sockets)
# ping3 requires root or setcap. Running as root is easiest for this demo.
RUN apt-get update && apt-get install -y iputils-ping curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
