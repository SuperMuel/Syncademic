FROM python:3.11-slim

# Set the working directory
WORKDIR /app


# Install build dependencies for packages that need compilation (hdbscan)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.7.3 /uv /uvx /bin/

# Copy only the dependency definition files.
COPY pyproject.toml uv.lock ./

# Install Python dependencies using uv.
# - `uv sync` installs dependencies specified in pyproject.toml and uv.lock.
# - `--frozen`: Ensures that uv uses the exact versions from uv.lock, providing reproducible builds.
RUN uv sync --frozen --no-dev --no-cache

# Copy the rest of the application code.
COPY . .

# --- Production Security Best Practice: Run as a non-root user ---
# Create a non-root user and group for running the application.
# Running as root inside the container is a security risk.
# The UID/GID (e.g., 1001) can be any non-zero value not already in use.
RUN groupadd -r appgroup && useradd --no-log-init -r -g appgroup -u 1001 appuser

# Change ownership of application files to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to the non-root user.
USER appuser

# Set environment variable for port with a default value
ENV PORT=80

# Expose the port defined by the environment variable
EXPOSE ${PORT}

# Run the application using the environment variable
CMD ["/bin/sh", "-c", "/app/.venv/bin/fastapi run /app/backend/api.py --port ${PORT} --host 0.0.0.0"]
