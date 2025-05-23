FROM python:3.11-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.7.3 /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Needed because of the hdbscan dependency
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


COPY admin/ /app/admin/
COPY backend/ /app/backend/

# Install dependencies
WORKDIR /app/admin
RUN uv sync --frozen --no-dev --no-cache

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["uv", "run", "streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
