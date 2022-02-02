# FastAPI Auth Middleware

We at [Code Specialist](https://code-specialist.com) love FastAPI for its simplicity and feature-richness. Though we were a bit staggered by the poor documentation and integration
of auth-concepts. That's why we wrote a **FastAPI Auth Middleware**. It integrates seamlessly into FastAPI applications and requires minimum configuration. It is built
upon [Starlette](https://www.starlette.io/) and thereby requires **no dependencies** you do not have included anyway.

**Caution**: This is a middleware to plug in existing authentication. Even though we offer some sample code, this package assumes you already have a way to generate and verify
whatever you use, to authenticate your users. In most of the usual cases this will be an access token or bearer. For instances as in **OAuth2** or **Open ID Connect**.

## Install

```shell
pip install fastapi-auth-middleware
```

## Why FastAPI Auth Middlware?

- Application or Route scoped automatic authorization and authentication with the perks of dependency injection (But without inflated signatures due to `Depends()`)
- Lightweight without additional dependencies
- Easy to configure
- Easy to extend and adjust to specific needs
- Plug-and-Play feeling

## Examples

### Simple

**simple.py**

```python
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
    return request.user


if __name__ == '__main__':
    uvicorn.run('simple:app', host="0.0.0.0", port=8080)  # Starts the uvicorn ASGI
```

### Simple with scopes

**simple_with_scopes.py**

```python
from typing import Tuple, List
import uvicorn
from fastapi import FastAPI
from starlette.authentication import requires
from starlette.requests import Request

from fastapi_auth_middleware import AuthMiddleware, FastAPIUser


# The method you have to provide
def verify_authorization_header(auth_header: str) -> Tuple[List[str], FastAPIUser]:
    user = FastAPIUser(first_name="Code", last_name="Specialist", user_id=1)  # Usually you would decode the JWT here and verify its signature to extract the 'sub'
    scopes = ["admin"]  # You could for instance use the scopes provided in the JWT or request them by looking up the scopes with the 'sub' somewhere
    return scopes, user


app = FastAPI()
app.add_middleware(AuthMiddleware, verify_authorization_header=verify_authorization_header)  # Add the middleware with your verification method to the whole application


@app.get('/home')  # Sample endpoint (secured)
@requires("admin")  # Requires the role 'admin' (Will succeed)
def home(request: Request):
    return request.user  # Returns the user object that is injected into the request. The FastAPIUser in this case


@app.get('/poweruser')  # Sample endpoint (secured)
@requires(["admin", "poweruser"])  # Requires the roles 'admin' and 'poweruser' (Will fail)
def poweruser(request: Request):
    return request.user  # Returns the user object that is injected into the request. The FastAPIUser in this case


if __name__ == '__main__':
    uvicorn.run('simple_with_scopes:app', host="0.0.0.0", port=8080)  # Starts the uvicorn ASGI
```

### Protected and Unprotected Endpoints

Currently, there is no support for router level middleware in FastAPI. However, Starlette currently shifts
toward [supporting this feature](https://github.com/encode/starlette/pull/1464) and may support it soon. Once Starlette includes this and FastAPI adopts it, there will be a more
elegant solution to this. But the current solution is to mount multiple apps instead of routers:

**multiple.py**

```python
from typing import Tuple, List
import uvicorn
from fastapi import FastAPI
from starlette.authentication import requires
from starlette.requests import Request

from fastapi_auth_middleware import AuthMiddleware, FastAPIUser


# The method you have to provide
def verify_authorization_header(auth_header: str) -> Tuple[List[str], FastAPIUser]:
    user = FastAPIUser(first_name="Code", last_name="Specialist", user_id=1)  # Usually you would decode the JWT here and verify its signature to extract the 'sub'
    scopes = ["admin"]  # You could for instance use the scopes provided in the JWT or request them by looking up the scopes with the 'sub' somewhere
    return scopes, user


users_app = FastAPI()
users_app.add_middleware(AuthMiddleware, verify_authorization_header=verify_authorization_header)  # Add the middleware with your verification method to the whole application


@users_app.get('/')  # Sample endpoint (secured)
def home(request: Request):
    return request.user  # Returns the user object that is injected into the request. The FastAPIUser in this case


public_app = FastAPI()


@public_app.get('/home')  # Sample endpoint (not secured)
def home(request: Request):
    return 'Hello World'


app = FastAPI()
app.mount(path="/user", app=users_app)  # Expects an authorization header, due to the auth middleware
app.mount(path="/", app=public_app)  # Does not use any middleware

if __name__ == '__main__':
    uvicorn.run('multiple:app', host="0.0.0.0", port=8080)  # Starts the uvicorn ASGI
```

This will result in an protected endpoint at `http:localhost:8080/user/` and an unprotected one at  `http:localhost:8080/home/`.