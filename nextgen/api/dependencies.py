from nextgen.api.auth import AuthHandler
from nextgen.data.services import UserDbService


def resolve_user_service() -> UserDbService:
    return UserDbService()


def resolve_auth_handler() -> AuthHandler:
    return AuthHandler()
