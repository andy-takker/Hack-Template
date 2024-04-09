from enum import StrEnum, unique


@unique
class UserType(StrEnum):
    ADMIN = "ADMIN"
    REGULAR = "REGULAR"
