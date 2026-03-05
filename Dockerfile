# Use slim image to keep container size small — good SRE practice
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies first (layer caching — rebuilds are faster)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Don't run as root — security best practice
RUN useradd --create-home appuser
USER appuser

# Expose the port Flask runs on
EXPOSE 5000

# Run the app
CMD ["python", "-m", "app.main"]
