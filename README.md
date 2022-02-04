# FastAPI Auth Middleware

We at [Code Specialist](https://code-specialist.com) love FastAPI for its simplicity and feature-richness. Though we were a bit staggered by the poor documentation and integration
of auth-concepts. That's why we wrote a **FastAPI Auth Middleware**. It integrates seamlessly into FastAPI applications and requires minimum configuration. It is built
upon [Starlette](https://www.starlette.io/) and thereby requires **no dependencies** you do not have included anyway.

**Caution**: This is a middleware to plug in existing authentication. Even though we offer some sample code, this package assumes you already have a way to generate and verify
whatever you use, to authenticate your users. In most of the usual cases this will be an access token or bearer. For instance as in **OAuth2** or **Open ID Connect**.

## Install

```shell
pip install fastapi_auth_middleware
```

## Documentation
More detailed docs are available at [https://fastapi-auth-middleware.code-specialist.com](https://fastapi-auth-middleware.code-specialist.com).

## Why FastAPI Auth Middlware?

- Application or Route scoped automatic authorization and authentication with the perks of dependency injection (But without inflated signatures due to `Depends()`)
- Lightweight without additional dependencies
- Easy to configure
- Easy to extend and adjust to specific needs
- Plug-and-Play feeling

## Usage

The usage of this middleware requires you to provide a single function that validates a given authorization header. The middleware will extract the content of the `Authorization`
HTTP header and inject it into your function that returns a list of scopes and a user object. The list of scopes may be empty if you do not use any scope based concepts. The user
object must be a `BaseUser` or any inheriting class such as `FastAPIUser`. Thereby, your `verify_authorization_header` function must implement a signature that contains a string as
an input and a `Tuple` of a `List of strings` and a `BaseUser` as output:

```python
from typing import Tuple, List
from fastapi_auth_middleware import FastAPIUser
from starlette.authentication import BaseUser

...
# Takes a string that will look like 'Bearer eyJhbGc...'
def verify_authorization_header(auth_header: str) -> Tuple[List[str], BaseUser]: # Returns a Tuple of a List of scopes (string) and a BaseUser
    user = FastAPIUser(first_name="Code", last_name="Specialist", user_id=1)  # Usually you would decode the JWT here and verify its signature to extract the 'sub'
    scopes = []  # You could for instance use the scopes provided in the JWT or request them by looking up the scopes with the 'sub' somewhere
    return scopes, user
```

This function is then included as an keyword argument when adding the middleware to the app.

```python
from fastapi import FastAPI
from fastapi_auth_middleware import AuthMiddleware

...

app = FastAPI()
app.add_middleware(AuthMiddleware, verify_authorization_header=verify_authorization_header)
```

After adding this middleware, all requests will pass the `verify_authorization_header` function and contain the **scopes** as well as the **user object** as injected dependencies.
All requests now pass the `verify_authorization_header` method. You may also verify that users posses scopes with `requires`:

```python
from starlette.authentication import requires

...

@app.get("/")
@requires(["admin"])  # Will result in an HTTP 401 if the scope is not matched
def some_endpoint():
    ...
```

You are also able to use the `user` object you injected on the `request` object:

```python
from starlette.requests import Request

...

@app.get('/')
def home(request: Request):
    return f"Hello {request.user.first_name}"  # Assuming you use the FastAPIUser object
```

## Examples

Various examples on how to use this middleware are available
at [https://fastapi-auth-middleware.code-specialist.com/examples](https://fastapi-auth-middleware.code-specialist.com/examples)