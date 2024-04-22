from dataclasses import dataclass

from hack_template.common.exceptions import UserWithUsernameAlreadyExistsException
from hack_template.common.users.models import CreateUserModel, LoginUserModel
from hack_template.common.users.storage import UserStorage
from hack_template.rest.auth.base import IAuthProvider
from hack_template.rest.auth.models import AuthTokenModel, AuthUser
from hack_template.rest.auth.passgen import Passgen


@dataclass(frozen=True)
class UserDispatcher:
    user_storage: UserStorage
    passgen: Passgen
    auth_provider: IAuthProvider

    async def create(self, new_user: CreateUserModel) -> AuthTokenModel:
        if await self.user_storage.get_by_username(username=new_user.username):
            raise UserWithUsernameAlreadyExistsException(
                username=new_user.username,
            )
        user = await self.user_storage.create(
            username=new_user.username,
            password_hash=self.passgen.hash(new_user.password),
            properties={
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
            },
        )
        token = self.auth_provider.generate_token(
            user=AuthUser(id=user.id, type=user.type),
        )
        return AuthTokenModel(token=token)

    async def login(self, login_user: LoginUserModel) -> AuthTokenModel | None:
        user = await self.user_storage.get_by_username_and_password_hash(
            username=login_user.username,
            password_hash=self.passgen.hash(login_user.password),
        )
        if user is None:
            return None
        token = self.auth_provider.generate_token(
            user=AuthUser(id=user.id, type=user.type),
        )
        return AuthTokenModel(token=token)
