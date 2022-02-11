from datetime import datetime, timedelta

from _pytest.fixtures import fixture
from fastapi import FastAPI
from jose import jwt
from starlette.authentication import requires
from starlette.requests import Request
from starlette.testclient import TestClient
from fastapi_auth_middleware import FastAPIUser, OAuth2Middleware

PRIVATE_KEY = """
-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----
"""

PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAzRXlseit3ivhop6LMeSt
msHgZ9bhohq5iW8Q38dWT/SWjgIML7MGDVFMCjLL0/duOo3k+Rcz83p0MXlkcJ+4
rup9cWv/C4PoJIGuGI5gjyt0NhNDMjSHEaIfxQaQRcd5ADdeYIzgB8B1ik95Me/U
h9J+4Q9Ldx/Pb0+d+2MslsHxR6RTKZKQzo/m5HwAi/n5dFro/XfKTrnlgyS+iCiw
qXCFzIrXI/nxWbCeO/0bYsRBAhWOr9eXT5+AXMTbLduv5FLLja+JlwDdJPbrr7aD
RSUNqS8Z3P+pFC1iURnXopiopuR60jIqbUgBYpDPjy37gNrG7moWefyc3w/yAE4P
3V9dSt1S6kDVktQdA7YpiXvznIGJqpBMcVYn4PjFp0BTB/XfcCXD1CV750Ty62WY
1S75uuR945W62BUBQHigiWUW2qttfaTNQC2jDfkOiNa6qnY99jz/GBfRiATAyiB/
Z5xZMB9T2jTyeDtTQWYejM9TPhP0Pge28grklT6wanMc27ICZWp4oyFlCFWCf02g
yz8Ium1Vf5zv2wFa4K9tQIWAz3K2Rurt7C+nmEDPFumBf9KMVjXhVRvOxo+2W8LF
T2IPGy+jDZoVFsVoOKylbJDm2uHmEH0NRUupecZog0vnClsN4/FQRYHhddOv55Jr
43ok0YBXU1kI8Li8izRRejsCAwEAAQ==
-----END PUBLIC KEY-----
"""


def sign_token(content: dict):
    return jwt.encode(content, key=PRIVATE_KEY, algorithm='RS256')


#  Sample app with simple routes, takes a verify_authorization_header callable that is applied to the middleware
def fastapi_app():
    app = FastAPI()
    app.add_middleware(OAuth2Middleware, public_key=PUBLIC_KEY, algorithms='RS256')

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
            "sub": "1",
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
