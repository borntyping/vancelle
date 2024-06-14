default:
  flask run

test:
  pytest

lint:
  mypy .

dist:
  make

sass:
  make "vancelle/static/dist/style.scss"
