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
ARG DART_VERSION=1.69.5
ARG DART_ARCH=x64
ADD https://github.com/sass/dart-sass/releases/download/${DART_VERSION}/dart-sass-${DART_VERSION}-linux-${DART_ARCH}.tar.gz /opt/
RUN tar -C /opt/ -xzvf /opt/dart-sass-${DART_VERSION}-linux-${DART_ARCH}.tar.gz
WORKDIR /opt/app
COPY package.json package-lock.json ./
RUN npm ci
COPY vancelle/static/src/ /opt/app/vancelle/static/src
RUN /opt/dart-sass/sass --load-path=node_modules "/opt/app/vancelle/static/src/style.scss:/opt/app/vancelle/static/dist/style.css"

#
# Configure the final image and copy files from build stages.
#
FROM base as final
WORKDIR /opt/app
ENTRYPOINT ["poetry", "run"]
ENV FLASK_APP="vancelle.app:create_personal_app()" \
    VANCELLE_CACHE_PATH="/var/cache/vancelle"
CMD gunicorn "vancelle.app:create_personal_app()" --access-logfile=-
EXPOSE 5000
VOLUME '/var/cache/vancelle'
COPY --from=build /opt/app/.venv /opt/app/.venv
COPY --from=sass /opt/app/vancelle/static/dist/ /opt/app/vancelle/static/dist/
COPY poetry.lock pyproject.toml ./
COPY vancelle/ vancelle/
