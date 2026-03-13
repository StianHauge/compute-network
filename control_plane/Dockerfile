FROM python:3.10-slim

WORKDIR /app

# Install dependencies needed for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY control_plane/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY control_plane ./control_plane
COPY shared ./shared

ENV PYTHONPATH=/app

EXPOSE 8000

# Run the API server
CMD ["uvicorn", "control_plane.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
