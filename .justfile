default:
  flask --app 'vancelle.app:create_personal_app()' run

sass:
  dart-sass --load-path "node_modules" "vancelle/static/src/style.scss:vancelle/static/dist/style.css"

test:
  pytest
