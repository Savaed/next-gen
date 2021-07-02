from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from nextgen.data.dbmodels import User


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


@dataclass
class AccessToken:
    exp: datetime
    iat: datetime
    sub: str
    username: str
    roles: list[UserRole]


class AuthHandler:
    def __init__(self) -> None:
        self._context = CryptContext(["bcrypt"], deprecated="auto")
        self._jwt_secret = "cesdfgldkfjglkdjfkl3465345glkdfjgld"

    def get_hash(self, password: str) -> str:
        return self._context.hash(password)

    def verify(self, password: str, hashed_password: str) -> bool:
        return self._context.verify(password, hashed_password)

    def encode_jwt(self, user: User) -> str:
        now = datetime.now()
        token = AccessToken(now + timedelta(hours=8), now, str(user.id), user.username, user.roles)
        return jwt.encode(asdict(token), self._jwt_secret)

    def decode_jwt(self, token: str) -> dict[str, Any]:
        try:
            token = jwt.decode(token, self._jwt_secret, algorithms=["HS256"])
            return token
        except jwt.ExpiredSignatureError:
            raise HTTPException(HTTP_401_UNAUTHORIZED, "Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(HTTP_401_UNAUTHORIZED, "Token is invalid")


class Authorization:
    def __init__(self, roles: list[UserRole] = None) -> None:
        self._roles = roles

    def __call__(self, auth: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> None:
        token = AuthHandler().decode_jwt(auth.credentials)

        if self._roles != None and not set(self._roles).issubset(set(token["roles"])):
            raise HTTPException(HTTP_403_FORBIDDEN, "Access denied. Insufficient permissions")


class AuthorizationPolicy:
    USER = Depends(Authorization([UserRole.USER]))
    ADMIN = Depends(Authorization([UserRole.ADMIN]))
