# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies (without dev dependencies)
RUN poetry install --without dev --no-root

# Copy the backend code
COPY . .

# Expose the port the app will run on
EXPOSE 5050

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5050", "wsgi:app"]