from dataclasses import dataclass

from pydantic import BaseModel

from hack_template.common.users.base import UserType


@dataclass
class AuthUser:
    id: int
    type: UserType


class AuthTokenModel(BaseModel):
    token: str
