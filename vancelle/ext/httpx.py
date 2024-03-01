import dataclasses
import typing

import httpx


@dataclasses.dataclass()
class BearerAuth(httpx.Auth):
    token: str = dataclasses.field(repr=False)

    def auth_flow(self, request: httpx.Request) -> typing.Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request
