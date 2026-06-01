# 1. Use an official Python image as a starting point
FROM python:3.10-slim

# 2. Set the "Folder" inside the container where we will work
WORKDIR /app

# 3. Copy our "Parts List" and install the tools
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy our actual script into the container
COPY ingest_weather.py .

# 5. The command to run when the container starts
CMD ["python", "ingest_weather.py"]