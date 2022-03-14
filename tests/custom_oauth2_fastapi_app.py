from datetime import datetime, timedelta

from fastapi import FastAPI
from jose import jwt
from starlette.authentication import AuthCredentials, requires
from starlette.requests import Request

from fastapi_auth_middleware import OAuth2Middleware, FastAPIUser
from tests.keys import PUBLIC_KEY, PRIVATE_KEY


def get_scopes(decoded_token: dict):
    try:
        return decoded_token["scope"].split(" ")
    except KeyError or AttributeError:
        return []


def get_user(decoded_token: dict):
    user_id = decoded_token.get("sub")
    try:
        first_name, last_name = decoded_token.get("name").split(" ")
        return FastAPIUser(first_name=first_name, last_name=last_name, user_id=user_id)
    except AttributeError:
        return FastAPIUser(first_name="did not specify", last_name="any name", user_id=user_id)


def get_new_token(old_token: str):
    # Usually you would perform some kind of exchange with a lookup for the the refresh token here
    content = {
        "sub": "1",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),  # Valid for 1 hour
        "aud": "tests",
        "iss": "tests",
        "name": "Code Specialist",
        "scope": "a b c"
    }
    return jwt.encode(content, key=PRIVATE_KEY, algorithm='RS256')


app = FastAPI(title="OAuth2 FastAPI App")
app.add_middleware(OAuth2Middleware,
                   public_key=PUBLIC_KEY,
                   get_scopes=get_scopes,
                   get_user=get_user,
                   get_new_token=get_new_token,
                   decode_token_options={"verify_signature": True, "verify_aud": False}
                   )


@app.get("/")
def home():
    return 'Hello World'


@app.get("/scopes")
def scopes(request: Request):
    auth_credentials: AuthCredentials = request.auth
    return auth_credentials.scopes


@app.get("/a-scope")
@requires("a")
def a_scope_required(request: Request):
    user: FastAPIUser = request.user
    return f'{user.is_authenticated} {user.display_name} {user.identity}'


@app.get("/a-b-c-scope")
@requires(["a", "b", "c"])
def a_scope_required(request: Request):
    user: FastAPIUser = request.user
    return f'{user.is_authenticated} {user.display_name} {user.identity}'


@app.get("/d-scope")
@requires("d")
def a_scope_required(request: Request):
    user: FastAPIUser = request.user
    return f'{user.is_authenticated} {user.display_name} {user.identity}'
