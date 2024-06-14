.PHONY: default clean

default: \
vancelle/static/dist/bootstrap-icons/bootstrap-icons.css \
vancelle/static/dist/bootstrap-icons/fonts/bootstrap-icons.woff \
vancelle/static/dist/bootstrap-icons/fonts/bootstrap-icons.woff2 \
vancelle/static/dist/bootstrap/ \
vancelle/static/dist/bootstrap/bootstrap.bundle.min.js \
vancelle/static/dist/bootstrap/bootstrap.bundle.min.js.map \
vancelle/static/dist/htmx.org/ext/debug.js \
vancelle/static/dist/htmx.org/ext/loading-states.js \
vancelle/static/dist/htmx.org/htmx.min.js \
vancelle/static/dist/hyperscript.org/_hyperscript.min.js \
vancelle/static/dist/sentry/sentry-spotlight.js \
vancelle/static/dist/style.css

vancelle/static/dist/style.css: vancelle/static/src/style.scss
	sass --load-path "node_modules" --embed-sources "$^:$@"

vancelle/static/dist/%/:
	@mkdir -p "$@"

vancelle/static/dist/bootstrap/%:
	@mkdir -p "$(@D)"
	cp "node_modules/bootstrap/dist/js/$(@F)" "$(@)"

vancelle/static/dist/bootstrap-icons/%:
	@mkdir -p "$(@D)"
	cp "node_modules/bootstrap-icons/font/$(@F)" "$(@)"

vancelle/static/dist/bootstrap-icons/fonts/%:
	@mkdir -p "$(@D)"
	cp "node_modules/bootstrap-icons/font/fonts/$(@F)" "$(@)"

vancelle/static/dist/htmx.org/%:
	@mkdir -p "$(@D)"
	cp "node_modules/htmx.org/dist/$(@F)" "$(@)"

vancelle/static/dist/htmx.org/ext/%:
	@mkdir -p "$(@D)"
	cp "node_modules/htmx.org/dist/ext/$(@F)" "$(@)"

vancelle/static/dist/hyperscript.org/%:
	@mkdir -p "$(@D)"
	cp "node_modules/hyperscript.org/dist/$(@F)" "$(@)"

vancelle/static/dist/sentry/%:
	cp -r "node_modules/@spotlightjs/overlay/dist/." "vancelle/static/dist/sentry/"

clean:
	rm -r vancelle/static/dist || :
