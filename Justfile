default:
  flask run

test:
  pytest

lint:
  mypy .

dist:
  make

sass *flags:
  dart-sass --load-path "node_modules" --embed-sources "vancelle/static/src/style.scss:vancelle/static/dist/style.css" {{flags}}
