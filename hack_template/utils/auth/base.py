import abc
from dataclasses import dataclass
from http import HTTPStatus

from fastapi import HTTPException, Request

from hack_template.utils.auth.models import AuthUser
from hack_template.utils.users.base import UserType

AUTH_HEADER = "Authorization"
AUTH_COOKIE = "Authorization"


class IAuthProvider(abc.ABC):
    @abc.abstractmethod
    async def authorize(self, request: Request) -> AuthUser | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def generate_token(self, user: AuthUser) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class SecurityManager:
    auth_provider: IAuthProvider

    async def maybe_auth(self, request: Request) -> AuthUser | None:
        return await self.auth_provider.authorize(request)

    async def require_auth(
        self,
        request: Request,
        user_type: UserType | None = None,
    ) -> AuthUser:
        auth_user = await self.auth_provider.authorize(request)
        if auth_user is None:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Required authorization",
            )
        if user_type is not None and auth_user.type != user_type:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Forbidden",
            )
        return auth_user

    async def require_admin_auth(
        self,
        request: Request,
    ) -> AuthUser:
        return await self.require_auth(request, user_type=UserType.ADMIN)

    async def require_regular_auth(
        self,
        request: Request,
    ) -> AuthUser:
        return await self.require_auth(request, user_type=UserType.REGULAR)
