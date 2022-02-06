from _pytest.fixtures import fixture
from fastapi import FastAPI
from starlette.authentication import requires
from starlette.requests import Request
from starlette.testclient import TestClient

from fastapi_auth_middleware import AuthMiddleware, FastAPIUser


# Sample verification function, does nothing of effect
def verify_authorization_header_basic(auth_header: str):
    user = FastAPIUser(first_name="Code", last_name="Specialist", user_id=1)
    scopes = ["authenticated"]
    return scopes, user


async def verify_authorization_header_basic_admin_scope(auth_header: str):
    user = FastAPIUser(first_name="Code", last_name="Specialist", user_id=1)
    scopes = ["admin"]
    return scopes, user


#  Sample app with simple routes, takes a verify_authorization_header callable that is applied to the middleware
def fastapi_app(verify_authorization_header: callable):
    app = FastAPI()
    app.add_middleware(AuthMiddleware, verify_authorization_header=verify_authorization_header)

    @app.get("/")
    def home():
        return 'Hello World'

    @app.get("/user")
    def home(request: Request):
        user: FastAPIUser = request.user
        return f'{user.is_authenticated} {user.display_name} {user.identity}'

    @app.get("/admin-scope")
    @requires("admin")
    def admin_scope_required(request: Request):
        user: FastAPIUser = request.user
        return f'{user.is_authenticated} {user.display_name} {user.identity}'

    return app


class TestBasicBehaviour:
    """
    This is a pretty artificial example test but it covers all the functionality for now.
    """

    @fixture
    def client(self):
        app = fastapi_app(verify_authorization_header_basic)
        return TestClient(app)

    @fixture
    def client_with_scopes(self):
        app = fastapi_app(verify_authorization_header_basic_admin_scope)
        return TestClient(app)

    def test_home_fail_no_header(self, client):
        assert client.get("/").status_code == 400

    def test_home_succeed(self, client):
        assert client.get("/", headers={"Authorization": "ey.."}).status_code == 200

    def test_user_attributes(self, client):
        request = client.get("/user", headers={"Authorization": "ey.."})
        assert request.status_code == 200
        assert request.content == b'"True Code Specialist 1"'  # b'"{user.is_authenticated} {user.display_name} {user.identity}"'

    def test_scopes(self, client, client_with_scopes):
        assert client.get("/admin-scope", headers={"Authorization": "ey.."}).status_code == 403  # Does not contain the requested scope
        assert client_with_scopes.get("/admin-scope", headers={"Authorization": "ey.."}).status_code == 200  # Contains the requested scope
