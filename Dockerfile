FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy SWL project files
COPY *.py .
COPY *.md .

# Expose API port
EXPOSE 8000

# Run moltbook agent by default
CMD ["python", "moltbook_agent.py", "--mode", "server", "--port", "8000"]
