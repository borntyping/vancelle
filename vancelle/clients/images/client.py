import dataclasses
import io

import flask
import requests
import werkzeug.exceptions


@dataclasses.dataclass()
class ImageCache:
    session: requests.Session

    def as_response(self, url: str) -> flask.Response:
        response = self.session.get(url)
        response.raise_for_status()
        return flask.send_file(
            path_or_file=io.BytesIO(response.content),
            mimetype=response.headers["Content-Type"],
        )
