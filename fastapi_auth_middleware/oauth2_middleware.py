from abc import abstractmethod, ABC
from typing import Tuple, List

import jwt
from jwt import ExpiredSignatureError
from starlette.authentication import AuthenticationBackend, AuthCredentials, AuthenticationError, BaseUser
from starlette.datastructures import MutableHeaders
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Scope, Receive, Send, Message

from fastapi_auth_middleware import FastAPIUser


class OAuth2Middleware:

    def __init__(
            self,
            app: ASGIApp,
            get_new_token: callable,
            public_key: str,
            get_scopes: callable = None,
            get_user: callable = None,
            decode_token_options: dict = None,
            issuer: str = None,
            audience: str = None,
    ):
        """ Constructor if the OAuth2Middleware

        Args:
            app (ASGIApp): ASGI app, e.g. Starlette/FastAPI instance
            get_new_token (callable): Function that returns a new token with an old one. Takes an access token as input argument Most likely you have a refresh token stored
                                      somewhere to renew the token.
            public_key (str): Public key of your OAuth2 Service to verify the jwt's signature
            get_scopes (callable): Optional: A method that returns a list of scopes based on a decoded_token input. Default will extract scopes from the token.
            get_user (callable): Optional: A method that returns a user Object based on a decoded_token input. Default will create a basic user from the token.
            decode_token_options (dict): Optional: A dictionary of decode options. Possible options are: verify_iat, verify_nbf, verify_exp, verify_iss, verify_aud. Default is
                                         {"verify_exp": True, "verify_iat": True, "verify_nbf": False, "verify_iss": False, "verify_aud": False }
            issuer (str): The issuer of the jwt. Required if the "verify_iss" option is enabled
            audience (str): The audience of the jwt. Required if the "verify_aud" option is enabled
        """
        self.app = app
        self.backend: OAuth2Backend = OAuth2Backend(
            public_key=public_key,
            get_scopes=get_scopes,
            get_user=get_user,
            decode_token_options=decode_token_options,
            issuer=issuer,
            audience=audience,
        )
        self.get_new_token = get_new_token

    async def __call__(
            self,
            scope: Scope,
            receive: Receive,
            send: Send
    ):

        if scope["type"] not in ["http", "websocket"]:  # Filter for relevant requests
            await self.app(scope, receive, send)  # Bypass
            return

        connection = HTTPConnection(scope)  # Scoped connection

        try:

            scope["auth"], scope["user"] = await self.backend.authenticate(connection)  # Authentication
            await self.app(scope, receive, send)  # Token is valid

        except ExpiredSignatureError:

            old_token = connection.headers.get("Authorization")
            new_token = self.get_new_token(old_token)  # Get a new token

            async def send_with_new_access_token(message: Message) -> None:
                if message["type"] == "http.response.start":  # Ensure this isn't called before stack is to be closed
                    headers = MutableHeaders(scope=message)
                    headers.append("New-Access-Token", new_token)
                await send(message)

            await self.app(scope, receive, send_with_new_access_token)


class OAuth2Backend(AuthenticationBackend, ABC):
    """ OAuth2 Backend """

    def __init__(
            self,
            public_key: str,
            get_scopes: callable,
            get_user: callable,
            decode_token_options: dict,
            issuer: str,
            audience: str
    ):
        """

        Args:
            public_key (str): Public key of your OAuth2 Service to verify the jwt's signature
            get_scopes (callable): Optional: A method that returns a list of scopes based on a decoded_token input. Default will extract scopes from the token.
            get_user (callable): Optional: A method that returns a user Object based on a decoded_token input. Default will create a basic user from the token.
            decode_token_options (dict): Optional: A dictionary of decode options. Possible options are: verify_iat, verify_nbf, verify_exp, verify_iss, verify_aud. Default is
                                         {"verify_exp": True, "verify_iat": True, "verify_nbf": False, "verify_iss": False, "verify_aud": False }
            issuer (str): The issuer of the jwt. Required if the "verify_iss" option is enabled
            audience (str): The audience of the jwt. Required if the "verify_aud" option is enabled
        """
        self.public_key = public_key
        self.issuer = issuer
        self.audience = audience

        if get_scopes is None:
            self.get_scopes = self._get_scopes  # Default fallback
        else:
            self.get_scopes = get_scopes

        if get_user is None:
            self.get_user = self._get_user  # Default fallback
        else:
            self.get_user = get_user

        if decode_token_options is None:
            self.decode_token_options = {
                "verify_exp": True,  # Expiry
                "verify_iat": True,  # Issued at
                "verify_nbf": False,  # Not Before
                "verify_iss": False,  # Issuer
                "verify_aud": False,  # Audience
            } # Default fallback
        else:
            self.decode_token_options = decode_token_options

    @staticmethod
    def _get_scopes(decoded_token: dict) -> List[str]:
        """ Default method if not method for getting scopes is passed

        Args:
            decoded_token (dict): A decoded JWT

        Returns:
            List[str]: List of scopes. Empty list if none set
        """
        try:
            return decoded_token["scopes"]
        except KeyError:  # Token does not define any scopes
            return []

    @staticmethod
    def _get_user(decoded_token: dict) -> FastAPIUser:
        """ Default method if not method for getting the user is passed

        Args:
            decoded_token (dict): A decoded JWT

        Returns:
            FastAPIUser: A FastAPIUser instance with basic attributes
        """
        try:
            name_segments = decoded_token.get("name").split(" ")
            first_name, last_name = name_segments[0], name_segments[-1]

        except AttributeError:  # Name isn't set
            first_name, last_name = None, None

        return FastAPIUser(user_id=decoded_token.get("sub"), first_name=first_name, last_name=last_name)

    @abstractmethod
    async def authenticate(self, conn: HTTPConnection) -> Tuple[AuthCredentials, BaseUser]:
        """ The authenticate method is invoked each time a route is called that the middleware is applied to.

        Args:
            conn (HTTPConnection): An HTTP connection of FastAPI/Starlette

        Returns:
            Tuple[AuthCredentials, BaseUser]: A tuple of AuthCredentials (scopes) and a user object that is or inherits from BaseUser
        """
        if "Authorization" not in conn.headers:
            raise AuthenticationError("Authorization header missing")

        auth_header = conn.headers["Authorization"]
        token = auth_header.split(" ")[-1]  # Generic approach: "Bearer eyJsn..." -> "eyJsn...", "Access Token eyJsn..." -> "eyJsn..."
        decoded_token = jwt.decode(jwt=token, key=self.public_key, options=self.decode_token_options, audience=self.audience, issuer=self.issuer)

        scopes = self.get_scopes(decoded_token)
        user = self.get_user(decoded_token)

        return AuthCredentials(scopes=scopes), user
