from collections.abc import AsyncGenerator, Sequence
from http import HTTPMethod

from aiomisc_dependency import dependency
from fastapi.middleware import Middleware
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from starlette.middleware.cors import CORSMiddleware

from hack_template.rest.args import RESTParser
from hack_template.utils.auth.base import (
    AUTH_COOKIE,
    AUTH_HEADER,
    IAuthProvider,
    SecurityManager,
)
from hack_template.utils.auth.jwt import JwtAuthProvider, JwtProcessor
from hack_template.utils.auth.passgen import Passgen
from hack_template.utils.db import (
    create_async_engine,
    create_async_session_factory,
)
from hack_template.utils.users.dispatcher import UserDispatcher
from hack_template.utils.users.storage import UserStorage


def config_deps(parser: RESTParser) -> None:  # noqa: C901
    @dependency
    async def engine() -> AsyncGenerator[AsyncEngine, None]:
        engine = create_async_engine(
            connection_uri=str(parser.db.pg_dsn),
            echo=parser.debug,
            pool_pre_ping=True,
        )
        yield engine
        await engine.dispose()

    @dependency
    def session_factory(
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return create_async_session_factory(engine=engine)

    @dependency
    def jwt_processor() -> JwtProcessor:
        return JwtProcessor(
            private_key=parser.security.private_key,
        )

    @dependency
    def auth_provider(jwt_processor: JwtProcessor) -> JwtAuthProvider:
        return JwtAuthProvider(
            jwt_processor=jwt_processor,
            auth_header=AUTH_HEADER,
            auth_cookie=AUTH_COOKIE,
        )

    @dependency
    def security_manager(auth_provider: IAuthProvider) -> SecurityManager:
        return SecurityManager(auth_provider=auth_provider)

    @dependency
    def passgen() -> Passgen:
        return Passgen(secret=parser.security.secret)

    @dependency
    def user_storage(
        session_factory: async_sessionmaker[AsyncSession],
    ) -> UserStorage:
        return UserStorage(session_factory=session_factory)

    @dependency
    def cors_middleware() -> Middleware:
        return Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=[
                HTTPMethod.OPTIONS,
                HTTPMethod.GET,
                HTTPMethod.HEAD,
                HTTPMethod.POST,
                HTTPMethod.DELETE,
            ],
            allow_headers=["*"],
        )

    @dependency
    def middlewares(
        cors_middleware: Middleware,
    ) -> Sequence[Middleware]:
        return (cors_middleware,)

    @dependency
    def user_dispatcher(
        user_storage: UserStorage, auth_provider: IAuthProvider, passgen: Passgen
    ) -> UserDispatcher:
        return UserDispatcher(
            user_storage=user_storage, auth_provider=auth_provider, passgen=passgen
        )
