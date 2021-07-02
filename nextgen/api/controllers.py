from datetime import datetime

from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from nextgen.api import dependencies as deps
from nextgen.api.auth import AuthHandler, UserRole
from nextgen.api.models.reponses import ApiResponse
from nextgen.api.models.requests import AuthCredentials
from nextgen.data.dbmodels import User
from nextgen.data.services import UserDbService


controller = cbv
auth_router = InferringRouter()


@controller(auth_router)
class AuthController:
    user_service: UserDbService = Depends(deps.resolve_user_service)
    auth_handler: AuthHandler = Depends(deps.resolve_auth_handler)

    @auth_router.post("/api/auth/register", status_code=HTTP_201_CREATED)
    async def register_user(self, auth: AuthCredentials) -> ApiResponse[str]:
        usernames = [user.username for user in self.user_service.get_all()]

        if auth.username in usernames:
            raise HTTPException(HTTP_400_BAD_REQUEST, f"{auth.username=}' is already taken")

        user = User(auth.username, self.auth_handler.get_hash(auth.password), [UserRole.USER])
        user.id = self.user_service.add(user)
        token = self.auth_handler.encode_jwt(user)
        return ApiResponse(token)

    @auth_router.post("/api/auth/login")
    async def login(self, auth: AuthCredentials) -> ApiResponse[str]:
        user = self.user_service.get_by_username(auth.username)

        if user is None:
            raise HTTPException(HTTP_400_BAD_REQUEST, f"User '{auth.username}' does not exist")

        if self.auth_handler.verify(auth.password, user.hashed_password):
            token = self.auth_handler.encode_jwt(user)
            return ApiResponse(token)

        raise HTTPException(HTTP_400_BAD_REQUEST, "Invalid password")
