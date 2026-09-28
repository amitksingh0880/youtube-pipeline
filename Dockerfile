FROM python:3.11-slim

# Install FFmpeg and required system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code and configs
COPY src/ ./src/
COPY config/ ./config/
COPY niches/ ./niches/
COPY data/ ./data/

# Create output directories for ephemeral processing
RUN mkdir -p data/output data/cache data/db

# Expose the port (Render uses 10000 by default or reads PORT env)
EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "src.ui.server:app", "--host", "0.0.0.0", "--port", "8000"]
