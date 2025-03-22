# syntax=docker/dockerfile:1
FROM fedora:40 AS base
ENV PATH=/root/.local/bin:$PATH \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    PYTHONUNBUFFERED=1

RUN dnf install -y \
    ca-certificates \
    poetry \
    postgresql \
    python3.12 \
 && dnf clean all \
 && rm -rf /var/cache/dnf

#
# Install Python dependencies.
#
FROM base AS build
WORKDIR /opt/app
COPY poetry.lock pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/pip \
    poetry install --no-root --only main,server

#
# Build style.css using npm and dart-sass.
#
FROM fedora:40 AS sass
RUN dnf install -y \
    make \
    nodejs \
    nodejs-npm \
 && dnf clean all \
 && rm -rf /var/cache/dnf
ARG DART_VERSION=1.69.5
ARG DART_ARCH=x64
ADD "https://github.com/sass/dart-sass/releases/download/${DART_VERSION}/dart-sass-${DART_VERSION}-linux-${DART_ARCH}.tar.gz" "/opt/"
RUN tar -C /opt/ -xzvf "/opt/dart-sass-${DART_VERSION}-linux-${DART_ARCH}.tar.gz"
ENV PATH="/opt/dart-sass/:$PATH"
WORKDIR /opt/app
COPY "Makefile" "package.json" "package-lock.json" ./
RUN npm ci
COPY "src/vancelle/assets/" "src/vancelle/assets/"
RUN make default

#
# Configure the final image and copy files from build stages.
#
FROM base AS final
WORKDIR /opt/app
COPY --from=build /opt/app/.venv /opt/app/.venv
COPY --from=sass /opt/app/src/vancelle/static/dist/ /opt/app/src/vancelle/static/dist/
COPY poetry.lock pyproject.toml ./
COPY src/ src/

ENTRYPOINT ["poetry", "run"]
CMD ["gunicorn", "vancelle.app:create_app()", "--access-logfile=-", "--bind=0.0.0.0:8000"]
ENV PYTHONPATH="/opt/app/src" \
    FLASK_APP="vancelle.app:create_app()" \
    VANCELLE_CACHE_PATH="/var/cache/vancelle"
EXPOSE 8000
VOLUME '/var/cache/vancelle'
