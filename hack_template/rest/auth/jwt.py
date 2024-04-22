from dataclasses import asdict, dataclass
from functools import cached_property
from typing import Any

import jwt
from fastapi import Request

from hack_template.rest.auth.base import IAuthProvider
from hack_template.rest.auth.models import AuthUser
from hack_template.rest.auth.rsa import parse_private_key, stringify_public_key

ALGORITHM = "RS256"


@dataclass(frozen=True)
class JwtProcessor:
    private_key: str

    def encode(self, payload: dict[str, Any]) -> str:
        return jwt.encode(
            payload=payload,
            key=self.private_key,
            algorithm=ALGORITHM,
        )

    def decode(self, token: str) -> dict[str, Any] | None:
        try:
            return jwt.decode(
                jwt=token,
                key=self.public_key,
                algorithms=[ALGORITHM],
            )
        except jwt.PyJWTError:
            return None

    @cached_property
    def public_key(self) -> str:
        rsa_private_key = parse_private_key(self.private_key)
        return stringify_public_key(rsa_private_key.public_key())


@dataclass(frozen=True)
class JwtAuthProvider(IAuthProvider):
    jwt_processor: JwtProcessor
    auth_header: str
    auth_cookie: str

    async def authorize(self, request: Request) -> AuthUser | None:
        token = self._get_token(request)
        if token is None:
            return None
        payload = self.jwt_processor.decode(token)
        if payload is None:
            return None
        return AuthUser(**payload)

    async def generate_token(self, user: AuthUser) -> str:
        return self.jwt_processor.encode(asdict(user))

    def _get_token(self, request: Request) -> str | None:
        return self._get_token_from_headers(request) or request.cookies.get(
            self.auth_cookie
        )

    def _get_token_from_headers(self, request: Request) -> str | None:
        raw_value = request.headers.get(self.auth_header)
        if raw_value is None:
            return None
        first, _, second = raw_value.partition(" ")
        return second or first
