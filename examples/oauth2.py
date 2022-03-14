import uvicorn
from fastapi import FastAPI
from starlette.requests import Request

from fastapi_auth_middleware import OAuth2Middleware


def get_public_key():
    with open("key.pem") as keyfile:
        return keyfile.readlines()


app = FastAPI()
# Add the middleware with a public key for your JWT signer
app.add_middleware(OAuth2Middleware, public_key=get_public_key())


@app.get('/')  # Sample endpoint (secured)
def home(request: Request):
    return request.user  # Returns the user object that is injected into the request. The FastAPIUser in this case


if __name__ == '__main__':
    uvicorn.run('oauth2:app', host="0.0.0.0", port=8080)  # Starts the uvicorn ASGI
