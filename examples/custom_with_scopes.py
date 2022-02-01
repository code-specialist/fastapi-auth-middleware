from typing import Tuple, List

import uvicorn
from fastapi import FastAPI
from starlette.authentication import requires
from starlette.requests import Request

from fastapi_auth_middleware import AuthMiddleware, FastAPIUser


def verify_authorization_header(auth_header: str) -> Tuple[List[str], FastAPIUser]:
    scopes = ["admin"]
    user = FastAPIUser(first_name="Yannic", last_name="Schröer", user_id=1)
    return scopes, user


app = FastAPI()
app.add_middleware(AuthMiddleware, verify_authorization_header=verify_authorization_header)


@app.get('/admin')
@requires(["admin"])
def admin(request: Request):
    return request.user


@app.get('/superadmin')
@requires(["superadmin"])
def superadmin(request: Request):
    return request.user


if __name__ == '__main__':
    uvicorn.run('example:app', host="0.0.0.0", port=8080)
