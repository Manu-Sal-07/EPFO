FROM python:3.12-slim AS base

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

FROM base AS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

FROM dependencies AS development
COPY . /app
EXPOSE 8000
CMD ["uvicorn", "pfcompass.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

COPY . /app

RUN addgroup --system pfcompass && adduser --system --group pfcompass
USER pfcompass

EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn pfcompass.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
