from fastapi.security import APIKeyHeader

from hack_template.rest.auth.base import AUTH_HEADER


class GetSessionFactory:
    pass


class GetUserStorage:
    pass


class GetUserDispatcher:
    pass


class MaybeAuth(APIKeyHeader):
    pass


class RequireAuth(APIKeyHeader):
    pass


class RequireAdminAuth(APIKeyHeader):
    pass


class RequireRegularAuth(APIKeyHeader):
    pass


MAYBE_AUTH = MaybeAuth(name=AUTH_HEADER)
REQUIRE_AUTH = RequireAuth(name=AUTH_HEADER)
REQUIRE_ADMIN_AUTH = RequireAdminAuth(name=AUTH_HEADER)
REQUIRE_REGULAR_AUTH = RequireRegularAuth(name=AUTH_HEADER)
