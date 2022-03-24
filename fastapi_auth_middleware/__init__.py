""" Lightweight auth middleware for FastAPI that just works. Fits most auth workflows with only a few lines of code. """

__version__ = "1.0.1"

from fastapi_auth_middleware.middleware import FastAPIUser, AuthMiddleware
from fastapi_auth_middleware.oauth2_middleware import OAuth2Middleware

__all__ = [FastAPIUser.__name__, AuthMiddleware.__name__, OAuth2Middleware.__name__]
