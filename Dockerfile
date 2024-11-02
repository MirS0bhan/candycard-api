# Use the official Python 3.11 image as the base
FROM python:3.12-slim

# Set environment variables to prevent Python from writing .pyc files and to buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system and Poetry dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory in the container
WORKDIR /app

# Copy only the pyproject.toml and poetry.lock to leverage Docker cache
COPY pyproject.toml poetry.lock ./

# Install Python dependencies using Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copy the rest of the application code
COPY . .

# Run the FastAPI application using uvicorn
CMD ["uvicorn", "candycard.app:app", "--host", "0.0.0.0", "--port", "8000"]
