FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:0.11.14 /uv /uvx /bin/

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy the app code to the image
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Run the app
CMD ["uv", "run", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
