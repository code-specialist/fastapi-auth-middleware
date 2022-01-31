from typing import Tuple

from fastapi import FastAPI
from starlette.authentication import AuthenticationBackend, AuthCredentials, AuthenticationError, BaseUser
from starlette.middleware.authentication import AuthenticationMiddleware


class FastAPIUser(BaseUser):

    def __init__(self, first_name: str, last_name: str, user_id: any):
        self.first_name = first_name
        self.last_name = last_name
        self.user_id = user_id

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    @property
    def identity(self) -> str:
        return self.user_id


class FastAPIAuth(AuthenticationBackend):

    def __init__(self, verify_authorization_header):
        self.verify_authorization_header = verify_authorization_header

    async def authenticate(self, conn) -> Tuple[AuthCredentials, FastAPIUser]:
        if "Authorization" not in conn.headers:
            raise AuthenticationError("Authorization header missing")

        auth_header = conn.headers["Authorization"]
        scopes, user = self.verify_authorization_header(auth_header)

        return AuthCredentials(scopes=scopes), user


# Intentionally not named with lower snake case convention as this is a factory method returning a class. Should feel like a class.
def AuthMiddleware(app: FastAPI, verify_authorization_header: callable):
    return AuthenticationMiddleware(app, backend=FastAPIAuth(verify_authorization_header))
