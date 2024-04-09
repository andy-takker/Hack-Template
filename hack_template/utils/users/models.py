from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from hack_template.utils.pagination import MetaPaginationModel
from hack_template.utils.users.base import UserType


class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    updated_at: datetime
    id: int
    type: UserType
    username: str
    properties: Mapping[str, Any]


class ShortUserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: UserType
    username: str


class UserPaginationModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    meta: MetaPaginationModel
    items: Sequence[ShortUserModel]


class CreateUserModel(BaseModel):
    username: str
    password: str
    password2: str
    first_name: str
    last_name: str


class LoginUserModel(BaseModel):
    username: str
    password: str


class UpdateUserModel(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
