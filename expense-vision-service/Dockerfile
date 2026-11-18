# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    RELOAD=false

WORKDIR /app

# Tesseract is invoked by pytesseract. The OpenCV runtime libraries are also
# required when importing cv2 in a slim Python image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-eng \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install only locked production dependencies before copying application code,
# so Docker can reuse this layer when only source files change.
COPY pyproject.toml uv.lock ./
RUN pip install uv \
    && uv sync --frozen --no-dev --no-install-project

COPY src ./src

RUN groupadd --system app \
    && useradd --system --gid app --home-dir /app app \
    && chown -R app:app /app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD /app/.venv/bin/python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ['PORT'] + '/actuators/health', timeout=3)"

CMD ["/bin/sh", "-c", "exec /app/.venv/bin/uvicorn main:app --app-dir src --host 0.0.0.0 --port \"$PORT\""]
