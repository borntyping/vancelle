# syntax=docker/dockerfile:1
FROM docker.io/library/python:3.12-slim as base
ENV DEBIAN_FRONTEND=noninteractive \
    PATH="/root/.local/bin:$PATH" \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    PYTHONUNBUFFERED=1
RUN --mount=target=/var/lib/apt/lists,type=cache \
    --mount=target=/var/cache/apt,type=cache \
    apt-get update \
 && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    python3-poetry \
 && apt-get clean

FROM base as build
WORKDIR /opt/app
COPY ["poetry.lock", "pyproject.toml", "./"]
RUN --mount=type=cache,target=/root/.cache/pip \
    poetry install --no-root --only main,server

FROM base as final
WORKDIR /opt/app
ENTRYPOINT ["poetry", "run"]
ENV FLASK_APP="vancelle.app:create_personal_app()"
CMD ["gunicorn", "vancelle.app:create_personal_app()", "--access-logfile=-"]
EXPOSE 5000
COPY --from=build /opt/app/.venv /opt/app/.venv
COPY ["poetry.lock", "pyproject.toml", "./"]
COPY ["vancelle/", "vancelle/"]
