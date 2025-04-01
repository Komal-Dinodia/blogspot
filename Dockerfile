# Use the official Python 3.10.12 image
FROM python:3.10.12

# Set the working directory inside the container
WORKDIR /app

# Copy the project files into the container
COPY . /app/

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev gcc

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port 8003
EXPOSE 8003

# Run Django migrations and start the server
CMD ["gunicorn", "--bind", "0.0.0.0:8003", "blogspot.wsgi:application"]
