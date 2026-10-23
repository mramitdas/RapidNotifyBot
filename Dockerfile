# syntax=docker/dockerfile:1
FROM python:3.12-slim AS build

WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1
COPY requirements/prod.txt requirements/prod.txt
COPY requirements/base.txt requirements/base.txt
RUN pip install --prefix=/install -r requirements/prod.txt

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /app
COPY --from=build /install /usr/local
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini pyproject.toml ./
COPY requirements/base.txt requirements/prod.txt ./

USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
