import inspect
from typing import Tuple, Callable, List, Dict

from fastapi import FastAPI
from starlette.authentication import AuthenticationBackend, AuthCredentials, AuthenticationError, BaseUser
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection, Request
from starlette.responses import JSONResponse


class FastAPIUser(BaseUser):
    """ Sample API User that gives basic functionality """

    def __init__(self, first_name: str, last_name: str, user_id: any):
        """ FastAPIUser Constructor

        Args:
            first_name (str): The first name of the user
            last_name (str): The last name of the user
            user_id (any): The user id, most likely an integer or string
        """
        self.first_name = first_name
        self.last_name = last_name
        self.user_id = user_id

    @property
    def is_authenticated(self) -> bool:
        """ Checks if the user is authenticated. This method essentially does nothing, but it could implement session logic for example.

        Returns:
            bool: True if the user is authenticated
        """
        return True

    @property
    def display_name(self) -> str:
        """ Display name of the user """
        return f'{self.first_name} {self.last_name}'

    @property
    def identity(self) -> str:
        """ Identification attribute of the user """
        return self.user_id


class FastAPIAuthBackend(AuthenticationBackend):
    """ Auth Backend for FastAPI """

    def __init__(self, verify_header: Callable[[Dict], Tuple[List[str], BaseUser]], excluded_urls: List[str] = None):
        """ Auth Backend constructor. Part of an AuthenticationMiddleware as backend.

        Args:
            verify_header (callable): A function handle that returns a list of scopes and a BaseUser
            excluded_urls (List[str]): A list of URL paths (e.g. ['/login', '/contact']) the middleware should not check for user credentials ( == public routes)
        """
        self.verify_header = verify_header
        self.excluded_urls = [] if excluded_urls is None else excluded_urls

    async def authenticate(self, conn: HTTPConnection) -> Tuple[AuthCredentials, BaseUser]:
        """ The 'magic' happens here. The authenticate method is invoked each time a route is called that the middleware is applied to.

        Args:
            conn (HTTPConnection): An HTTP connection by FastAPI/Starlette

        Returns:
            Tuple[AuthCredentials, BaseUser]: A tuple of AuthCredentials (scopes) and a user object that is or inherits from BaseUser
        """
        if conn.url.path in self.excluded_urls:
            return AuthCredentials(scopes=[]), "Unauthenticated User"

        if "Authorization" not in conn.headers:
            raise AuthenticationError("Authorization header missing")

        try:
            if inspect.iscoroutinefunction(self.verify_header):
                scopes, user = await self.verify_header(conn.headers)
            else:
                scopes, user = self.verify_header(conn.headers)

        except Exception as exception:
            raise AuthenticationError(exception) from None

        return AuthCredentials(scopes=scopes), user


# noinspection PyPep8Naming
def AuthMiddleware(
        app: FastAPI,
        verify_header: Callable[[str], Tuple[List[str], BaseUser]],
        auth_error_handler: Callable[[Request, AuthenticationError], JSONResponse] = None,
        excluded_urls: List[str] = None
):
    """ Factory method, returning an AuthenticationMiddleware
    Intentionally not named with lower snake case convention as this is a factory method returning a class. Should feel like a class.

    Args:
        app (FastAPI): The FastAPI instance the middleware should be applied to. The `add_middleware` function of FastAPI adds the app as first argument by default.
        verify_header (Callable[[str], Tuple[List[str], BaseUser]]): A function handle that returns a list of scopes and a BaseUser
        auth_error_handler (Callable[[Request, Exception], JSONResponse]): Optional error handler for creating responses when an exception was raised in verify_authorization_header
        excluded_urls (List[str]): A list of URL paths (e.g. ['/login', '/contact']) the middleware should not check for user credentials ( == public routes)

    Examples:
        ```python
        def verify_authorization_header(auth_header: str) -> Tuple[List[str], FastAPIUser]:
            scopes = ["admin"]
            user = FastAPIUser(first_name="Code", last_name="Specialist", user_id=1)
            return scopes, user

        app = FastAPI()
        app.add_middleware(AuthMiddleware, verify_authorization_header=verify_authorization_header)
        ```
    """
    return AuthenticationMiddleware(app, backend=FastAPIAuthBackend(verify_header=verify_header, excluded_urls=excluded_urls), on_error=auth_error_handler)
