# Official Python image
FROM python:3.13.3-slim-bookworm

# Set working directory
WORKDIR /app

# Set working directory in the container 
COPY . .

# Install Python dependencies 
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Set the default command to run your main script
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
