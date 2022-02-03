""" Lightweight auth middleware for FastAPI that just works. Fits most auth workflows with only a few lines of code. """

__version__ = "0.1a0"

from fastapi_auth_middleware.middleware import FastAPIUser, AuthMiddleware

__all__ = [FastAPIUser.__name__, AuthMiddleware.__name__]
