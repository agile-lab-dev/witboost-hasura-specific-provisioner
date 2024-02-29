from typing import Generator

from httpx import Auth, Request, Response


class HasuraAdminTokenAuth(Auth):
    _admin_secret: str

    def __init__(self, admin_secret: str):
        self._admin_secret = admin_secret

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        request.headers["X-Hasura-Role"] = "admin"
        request.headers["X-Hasura-Admin-Secret"] = self._admin_secret
        yield request
