from fastapi import FastAPI
from starlette.authentication import AuthCredentials, requires
from starlette.requests import Request

from fastapi_auth_middleware import OAuth2Middleware, FastAPIUser
from tests.keys import PUBLIC_KEY


def get_scopes(auth_header: str):
    return ["a b c"]


def get_user(auth_header: str):
    return FastAPIUser(first_name="Code", last_name="Specialist", user_id=1)


def get_new_token(old_token: str):
    return "Some new token"


app = FastAPI(title="OAuth2 FastAPI App")
app.add_middleware(OAuth2Middleware, public_key=PUBLIC_KEY, get_scopes=get_scopes, get_user=get_user, get_new_token=get_new_token)


@app.get("/")
def home():
    return 'Hello World'


@app.get("/scopes")
def home(request: Request):
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
