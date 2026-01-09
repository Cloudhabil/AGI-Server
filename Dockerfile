FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY skills/ ./skills/
COPY core/ ./core/
COPY configs/ ./configs/
COPY agents/ ./agents/
COPY governor/ ./governor/
COPY hnet/ ./hnet/
COPY templates/ ./templates/
COPY static/ ./static/
COPY main.py interface.py run.py boot.py ./

# Install dependencies
RUN pip install --no-cache-dir .

# Create data directory for memories if not exists
RUN mkdir -p /app/data /app/skills/conscience/memory/store

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/status')" || exit 1

# Run the cognitive interface
CMD ["python", "main.py"]
