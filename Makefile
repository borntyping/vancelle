.PHONY: default clean

default: \
src/vancelle/static/dist/bootstrap-icons/bootstrap-icons.svg \
src/vancelle/static/dist/bootstrap-icons/font/bootstrap-icons.min.css \
src/vancelle/static/dist/bootstrap-icons/font/fonts/bootstrap-icons.woff \
src/vancelle/static/dist/bootstrap-icons/font/fonts/bootstrap-icons.woff2 \
src/vancelle/static/dist/bootstrap/ \
src/vancelle/static/dist/bootstrap/bootstrap.bundle.min.js \
src/vancelle/static/dist/bootstrap/bootstrap.bundle.min.js.map \
src/vancelle/static/dist/htmx.org/htmx.min.js \
src/vancelle/static/dist/htmx-ext-loading-states/loading-states.js \
src/vancelle/static/dist/hyperscript.org/_hyperscript.min.js \
src/vancelle/static/dist/sentry/sentry-spotlight.js \
src/vancelle/static/dist/style.css

src/vancelle/static/dist/style.css: src/vancelle/assets/style.scss
	sass --load-path "node_modules" --embed-sources "$^:$@"

src/vancelle/static/dist/%/:
	@mkdir -p "$@"

src/vancelle/static/dist/bootstrap/%:
	@mkdir -p "$(@D)"
	cp "node_modules/bootstrap/dist/js/$(@F)" "$(@)"

src/vancelle/static/dist/bootstrap-icons/%:
	@mkdir -p "$(@D)"
	cp "node_modules/bootstrap-icons/$(@F)" "$(@)"
src/vancelle/static/dist/bootstrap-icons/font/%:
	@mkdir -p "$(@D)"
	cp "node_modules/bootstrap-icons/font/$(@F)" "$(@)"
src/vancelle/static/dist/bootstrap-icons/font/fonts/%:
	@mkdir -p "$(@D)"
	cp "node_modules/bootstrap-icons/font/fonts/$(@F)" "$(@)"

src/vancelle/static/dist/htmx.org/%:
	@mkdir -p "$(@D)"
	cp "node_modules/htmx.org/dist/$(@F)" "$(@)"

src/vancelle/static/dist/htmx-ext-loading-states/%:
	@mkdir -p "$(@D)"
	cp "node_modules/htmx-ext-loading-states/$(@F)" "$(@)"

src/vancelle/static/dist/hyperscript.org/%:
	@mkdir -p "$(@D)"
	cp "node_modules/hyperscript.org/dist/$(@F)" "$(@)"

src/vancelle/static/dist/sentry/%:
	cp -r "node_modules/@spotlightjs/overlay/dist/." "src/vancelle/static/dist/sentry/"

clean:
	rm -r src/vancelle/static/dist || :
