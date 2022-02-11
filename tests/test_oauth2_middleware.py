from datetime import datetime, timedelta

from _pytest.fixtures import fixture
from fastapi import FastAPI
from jose import jwt
from starlette.authentication import requires
from starlette.requests import Request
from starlette.testclient import TestClient
from fastapi_auth_middleware import FastAPIUser, OAuth2Middleware

PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----"""

PUBLIC_KEY = """MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAnOBJH3FqGEWS4rn2mvwQ
LcosmZ06TBFI45yCt4ybpKMc4HdA3iO4q3I9fI/juMOGJqHjYvkuGiqUFxLfTkGw
91FRXkkRgeQ9M4ZpTpYSU+ju+JzBT35D3skmn617q/c1zciWRcIs1uQmsCEyyLk7
4MtgwY5nEe7G0nJs59k5q6j4jTUEJg3FCBhW8lEXpaHaKrU/aJgVbZ4YwHvMjLFE
oomUVTbGhXMEQ870Wp0QyYBtyQRn/yJAQ074ZF+M1uOXD8sFXfIhnc4+bi2DNj49
A64LbYrfVX0gkbTg7iiOg3wbmzm/If1PTQ03b2AJd46DusD+ymifJTvzuinh3dPP
zvevd2y082heuqIu4XKa1lcoAK1UdO/4TqnyYnsl8i9lcP19Hu3+p2HO/dg3Il17
t/SKdqffwT7Mf6KY15iDWXtn1vTdz+a0UUK9VehlJ0UdOIwHiWUyvqWS7UhOIziJ
/Ow5VTDM/K380xgcMcCq61kdqCV8QKZNUjoIiYBLOGuPDkRqmqZBEo5t2ys0BO9X
w3Q2xCORYREFysoo412j823pvXB0bvZh7wKsUwl8aidTkNItHS48tjW0LGtfc0rL
vrjLxT635bzWw4eXKqy2FNMyzMALK422MSMQF3Lzvj5fpj04olo++/HmzKiOc268
BjsdJHMjggGL/RT6ejrAPMUCAwEAAQ==""".replace("\n", "")


def sign_token(content: dict):
    return jwt.encode(content, key=PRIVATE_KEY)


#  Sample app with simple routes, takes a verify_authorization_header callable that is applied to the middleware
def fastapi_app():
    app = FastAPI()
    app.add_middleware(OAuth2Middleware, public_key=PUBLIC_KEY)

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


class TestOAuth2Middleware:
    """
    This is a pretty artificial example test but it covers all the functionality for now.
    """

    @fixture
    def sample_token(self):
        return sign_token({
            "sub": 1,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1),  # Valid for 1 hour
            "aud": "tests",
            "iss": "tests",
            "name": "Code Specialist",
            "scope": "a b c"
        })

    @fixture
    def client(self):
        app = fastapi_app()
        return TestClient(app)

    def test_home_fail_no_header(self, client):
        assert client.get("/").status_code == 401

    def test_home_succeed(self, client, sample_token):
        assert client.get("/", headers={"Authorization": f"Bearer {sample_token}"}).status_code == 200
