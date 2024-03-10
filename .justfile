default:
  flask --app 'vancelle.app:create_personal_app()' run

sass *flags:
  dart-sass --load-path "node_modules" --embed-sources "vancelle/static/src/style.scss:vancelle/static/dist/style.css" {{flags}}

test:
  pytest

lint:
  mypy .

docker-build:
  docker build -t vancelle .

docker-run: docker-build
  docker run vancelle flask

deploy:
  git push dokku
  git push origin
