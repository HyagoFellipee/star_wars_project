FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Cloud Run uses PORT env var (default 8080, but we use 8000)
ENV PORT=8000
EXPOSE 8000

# Run with production settings
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
