from collections.abc import AsyncGenerator, Sequence

import ujson
from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiomisc_dependency import dependency
from fastapi.middleware import Middleware
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from hack_template.args import Parser
from hack_template.bot.middlewares.deps import DepsMiddleware
from hack_template.bot.middlewares.user import UserMiddleware
from hack_template.common.telegram.storage import TelegramStorage
from hack_template.common.users.storage import UserStorage
from hack_template.db.utils import (
    create_async_engine,
    create_async_session_factory,
)
from hack_template.rest.auth.base import (
    AUTH_COOKIE,
    AUTH_HEADER,
    IAuthProvider,
    SecurityManager,
)
from hack_template.rest.auth.jwt import JwtAuthProvider, JwtProcessor
from hack_template.rest.auth.passgen import Passgen
from hack_template.rest.middlewares import get_cors_middleware
from hack_template.rest.users.dispatcher import UserDispatcher


def config_deps(parser: Parser) -> None:  # noqa: C901
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
        return get_cors_middleware()

    @dependency
    def rest_middlewares(
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

    @dependency
    def bot() -> Bot:
        return Bot(
            token=parser.telegram.bot_token,
            parse_mode=ParseMode.HTML,
        )

    @dependency
    def fsm_storage() -> BaseStorage:
        if parser.debug:
            return MemoryStorage()
        return RedisStorage.from_url(
            url=str(parser.redis.redis_dsn),
            key_builder=DefaultKeyBuilder(with_destiny=True),
            json_loads=ujson.loads,
            json_dumps=ujson.dumps,
        )

    @dependency
    def dispatcher(
        fsm_storage: BaseStorage,
    ) -> Dispatcher:
        return Dispatcher(
            storage=fsm_storage,
            events_isolation=SimpleEventIsolation(),
        )

    @dependency
    def telegram_storage(
        session_factory: async_sessionmaker[AsyncSession],
    ) -> TelegramStorage:
        return TelegramStorage(
            session_factory=session_factory,
        )

    @dependency
    def user_middleware(telegram_storage: TelegramStorage) -> BaseMiddleware:
        return UserMiddleware(telegram_storage=telegram_storage)

    @dependency
    def deps_middleware(
        user_storage: UserStorage,
        telegram_storage: TelegramStorage,
    ) -> BaseMiddleware:
        return DepsMiddleware(
            deps={
                "user_storage": user_storage,
                "telegram_storage": telegram_storage,
            },
        )

    @dependency
    def bot_middlewares(
        user_middleware: BaseMiddleware,
        deps_middleware: BaseMiddleware,
    ) -> Sequence[BaseMiddleware]:
        return (user_middleware, deps_middleware)
