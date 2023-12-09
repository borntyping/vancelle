Sentry
======

Dependencies
------------

Ensure the `debug` group of dependencies is installed.

```shell
poetry install --with=debug
```

Usage
-----

Run [Spotlight](https://spotlightjs.com/) in the background:

```shell
npx @spotlightjs/spotlight
```

Configure [Sentry](https://docs.sentry.io) in the Python code:

```python
import sentry_sdk

sentry_sdk.init(spotlight=True, enable_tracing=True)
```

Open the application, wait for the page to finish loading, and click the Spotlight button at the bottom right of the page.
