# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

RUN apt-get update && apt-get install -y curl
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi

# Install any needed packages for Vue.js application specified in package.json
WORKDIR /app/frontend
RUN npm install
RUN npm install
RUN npm run build

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Switch back to the main app directory
WORKDIR /app

# Run the application when the container launches
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]