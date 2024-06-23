# syntax=docker/dockerfile:1
FROM docker.io/library/python:3.12-slim as base
ENV DEBIAN_FRONTEND=noninteractive \
    PATH=/root/.local/bin:$PATH \
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
    postgresql-client \
    python3-poetry \
 && apt-get clean

#
# Install Python dependencies.
#
FROM base as build
WORKDIR /opt/app
COPY poetry.lock pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/pip \
    poetry install --no-root --only main,server

#
# Build style.css using npm and dart-sass.
#
FROM docker.io/library/node:current-slim as sass
RUN --mount=target=/var/lib/apt/lists,type=cache \
    --mount=target=/var/cache/apt,type=cache \
    apt-get update \
 && apt-get install -y --no-install-recommends make \
 && apt-get clean
ARG DART_VERSION=1.69.5
ARG DART_ARCH=x64
ADD https://github.com/sass/dart-sass/releases/download/${DART_VERSION}/dart-sass-${DART_VERSION}-linux-${DART_ARCH}.tar.gz /opt/
RUN tar -C /opt/ -xzvf /opt/dart-sass-${DART_VERSION}-linux-${DART_ARCH}.tar.gz
ENV PATH="/opt/dart-sass/:$PATH"
WORKDIR /opt/app
COPY "Makefile" "package.json" "package-lock.json" ./
COPY "src/vancelle/assets/" "src/vancelle/assets/"
RUN npm ci
RUN make

#
# Configure the final image and copy files from build stages.
#
FROM base as final
WORKDIR /opt/app
COPY --from=build /opt/app/.venv /opt/app/.venv
COPY --from=sass /opt/app/src/vancelle/static/dist/ /opt/app/src/vancelle/static/dist/
COPY poetry.lock pyproject.toml ./
COPY src/ src/

ENTRYPOINT ["poetry", "run"]
CMD gunicorn "vancelle.app:create_app()" --access-logfile=- --bind="0.0.0.0:8000"
ENV FLASK_APP="vancelle.app:create_app()" \
    VANCELLE_CACHE_PATH="/var/cache/vancelle"
EXPOSE 8000
VOLUME '/var/cache/vancelle'
