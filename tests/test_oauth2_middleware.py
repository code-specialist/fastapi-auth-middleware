from datetime import datetime, timedelta

import pytest
from _pytest.fixtures import fixture
from fastapi import FastAPI
from jose import jwt
from starlette.authentication import requires, AuthCredentials
from starlette.requests import Request
from starlette.testclient import TestClient
from fastapi_auth_middleware import FastAPIUser, OAuth2Middleware
from tests.basic_fastapi_app import app as basic_app
from tests.custom_oauth2_fastapi_app import app as oauth2_custom_app
from tests.keys import PRIVATE_KEY


def sign_token(content: dict):
    return jwt.encode(content, key=PRIVATE_KEY, algorithm='RS256')


class TestOAuth2Middleware:
    sample_scopes = "a b c"

    basic_client = TestClient(basic_app)
    custom_oauth2_client = TestClient(oauth2_custom_app)
    test_clients = [basic_client, custom_oauth2_client]

    @fixture
    def expired_token(self):
        return sign_token({
            "sub": "1",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() - timedelta(hours=1),  # Invalid since 1 hour
            "aud": "tests",
            "iss": "tests",
            "name": "Code Specialist",
            "scope": self.sample_scopes
        })

    @fixture
    def valid_token(self):
        return sign_token({
            "sub": "1",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1),  # Valid for 1 hour
            "aud": "tests",
            "iss": "tests",
            "name": "Code Specialist",
            "scope": self.sample_scopes
        })

    @pytest.mark.parametrize('client', test_clients)
    def test_home_fail_no_header(self, client):
        assert client.get("/").status_code == 401

    @pytest.mark.parametrize('client', test_clients)
    def test_home_succeed(self, client, valid_token):
        response = client.get("/", headers={"Authorization": f"Bearer {valid_token}"})
        assert response.status_code == 200

    @pytest.mark.parametrize('client', test_clients)
    def test_single_scope_required(self, client, valid_token):
        response = client.get("/a-scope", headers={"Authorization": f"Bearer {valid_token}"})
        assert response.status_code == 200

    @pytest.mark.parametrize('client', test_clients)
    def test_multiple_scopes_required(self, client, valid_token):
        response = client.get("/a-b-c-scope", headers={"Authorization": f"Bearer {valid_token}"})
        assert response.status_code == 200

    @pytest.mark.parametrize('client', test_clients)
    def test_insufficient_scope(self, client, valid_token):
        response = client.get("/d-scope", headers={"Authorization": f"Bearer {valid_token}"})
        assert response.status_code == 403  # Insufficient scope

    @pytest.mark.parametrize('client', test_clients)
    def test_scopes_set(self, client, valid_token):
        response = client.get("/scopes", headers={"Authorization": f"Bearer {valid_token}"})
        assert response.status_code == 200
        assert response.json() == self.sample_scopes.split(" ")

    @pytest.mark.parametrize('client', [basic_client])
    def test_token_expired(self, client, expired_token):
        response = client.get("/scopes", headers={"Authorization": f"Bearer {expired_token}"})
        assert response.status_code == 401

    @pytest.mark.parametrize('client', [custom_oauth2_client])
    def test_token_refreshed(self, client, expired_token):
        response = client.get("/scopes", headers={"Authorization": f"Bearer {expired_token}"})
        assert response.status_code == 200
