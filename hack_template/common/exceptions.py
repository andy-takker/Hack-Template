class HackTemplateException(Exception):
    pass


class UserWithUsernameAlreadyExistsException(HackTemplateException):
    def __init__(self, username: str) -> None:
        self.username = username

    @property
    def message(self) -> str:
        return f"User with username `{self.username}` already exists"
