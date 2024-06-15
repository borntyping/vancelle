# Run the Flask application.
default:
  flask run

# Run unit tests.
test:
  pytest

# Run Python linters.
lint:
  ruff check
  ruff format

# Build SCSS on changes.
sass:
  dart-sass --watch --load-path "node_modules" --embed-sources "src/vancelle/assets/style.scss:src/vancelle/static/dist/style.css"

# Run Spotlight for tracing.
spotlight:
  npx spotlight-sidecar

# Build dist/ directory.
dist:
  make
