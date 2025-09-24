# Dockerfile

# 1. Use an official lightweight Python image as a base
FROM python:3.9-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file and install dependencies
# This is done first to leverage Docker's layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app/download_nltk.py .
RUN python3 download_nltk.py

# 4. Copy the application code and assets into the container
COPY ./app/ .

RUN mkdir -p /app/assets

# 5. Expose the port the Flask app will run on
EXPOSE 5000

# 6. Define the command to run the application
ENTRYPOINT ["python3", "main.py"]
CMD ["--bundles", "all"]
