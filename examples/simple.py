from typing import Tuple, List
import uvicorn
from fastapi import FastAPI
from starlette.requests import Request

from fastapi_auth_middleware import AuthMiddleware, FastAPIUser


# The method you have to provide
def verify_authorization_header(auth_header: str) -> Tuple[List[str], FastAPIUser]:
    user = FastAPIUser(first_name="Code", last_name="Specialist", user_id=1)  # Usually you would decode the JWT here and verify its signature to extract the 'sub'
    scopes = []  # You could for instance use the scopes provided in the JWT or request them by looking up the scopes with the 'sub' somewhere
    return scopes, user


app = FastAPI()
app.add_middleware(AuthMiddleware, verify_authorization_header=verify_authorization_header)  # Add the middleware with your verification method to the whole application


@app.get('/')  # Sample endpoint (secured)
def home(request: Request):
    return request.user  # Returns the user object that is injected into the request. The FastAPIUser in this case


if __name__ == '__main__':
    uvicorn.run('example:app', host="0.0.0.0", port=8080)  # Starts the uvicorn ASGI
