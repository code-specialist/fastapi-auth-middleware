from typing import Callable, List, Dict

from _pytest.fixtures import fixture
from fastapi import FastAPI
from starlette.authentication import requires, AuthenticationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from fastapi_auth_middleware import AuthMiddleware, FastAPIUser


# Sample verification function, does nothing of effect
def verify_header(headers: Dict):
    user = FastAPIUser(first_name="Code", last_name="Specialist", user_id=1)
    scopes = ["authenticated"]
    return scopes, user


async def verify_header_basic_admin_scope(headers: List[str]):
    user = FastAPIUser(first_name="Code", last_name="Specialist", user_id=1)
    scopes = ["admin"]
    return scopes, user


def raise_exception_in_verify_authorization_header(_):
    raise Exception('some auth error occured')


#  Sample app with simple routes, takes a verify_authorization_header callable that is applied to the middleware
def fastapi_app(verify_header: Callable, auth_error_handler: Callable = None, excluded_urls: List[str] = None):
    app = FastAPI()
    app.add_middleware(AuthMiddleware, verify_header=verify_header, auth_error_handler=auth_error_handler, excluded_urls=excluded_urls)

    @app.get("/public")
    def public():
        return 'Hello Public World'

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
    def client(self) -> TestClient:
        app = fastapi_app(verify_header, excluded_urls=["/public"])
        return TestClient(app)

    @fixture
    def client_with_scopes(self) -> TestClient:
        app = fastapi_app(verify_header_basic_admin_scope)
        return TestClient(app)

    def test_home_fail_no_header(self, client: TestClient):
        assert client.get("/").status_code == 400

    def test_home_succeed(self, client: TestClient):
        assert client.get("/", headers={"Authorization": "ey.."}).status_code == 200

    def test_user_attributes(self, client: TestClient):
        request = client.get("/user", headers={"Authorization": "ey.."})
        assert request.status_code == 200
        assert request.content == b'"True Code Specialist 1"'  # b'"{user.is_authenticated} {user.display_name} {user.identity}"'

    def test_scopes(self, client: TestClient, client_with_scopes: TestClient):
        assert client.get("/admin-scope", headers={"Authorization": "ey.."}).status_code == 403  # Does not contain the requested scope
        assert client_with_scopes.get("/admin-scope", headers={"Authorization": "ey.."}).status_code == 200  # Contains the requested scope

    def test_fail_auth_error(self):
        app = fastapi_app(verify_header=raise_exception_in_verify_authorization_header)
        client_with_auth_error = TestClient(app=app)

        response = client_with_auth_error.get('/', headers={"Authorization": "ey.."})
        assert response.status_code == 400

    def test_fail_auth_error_with_custom_handler(self):
        def handle_auth_error(request: Request, exception: AuthenticationError):
            assert isinstance(exception, AuthenticationError)
            return JSONResponse(content={'message': str(exception)}, status_code=401)

        app = fastapi_app(verify_header=raise_exception_in_verify_authorization_header, auth_error_handler=handle_auth_error)
        client_with_auth_error = TestClient(app=app)

        response = client_with_auth_error.get('/', headers={"Authorization": "ey.."})
        assert response.status_code == 401

    def test_public_path(self, client):
        assert client.get("/public").status_code == 200

    def test_public_path_with_fragments(self, client):
        assert client.get("/public#abcdef").status_code == 200

    def test_public_path_with_query(self, client):
        assert client.get("/public?abcdef=x").status_code == 200
