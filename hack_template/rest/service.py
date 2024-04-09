from collections.abc import Callable, Sequence

from aiomisc.service.uvicorn import UvicornApplication, UvicornService
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.middleware import Middleware

from hack_template.api.router import router as api_router
from hack_template.utils.auth.base import SecurityManager
from hack_template.utils.exceptions import (
    HackTemplateException,
    UserWithUsernameAlreadyExistsException,
)
from hack_template.utils.rest.exception_handlers import (
    http_exception_handler,
    internal_server_error_handler,
    user_already_exists_handler,
)
from hack_template.utils.rest.overrides import (
    MAYBE_AUTH,
    REQUIRE_ADMIN_AUTH,
    REQUIRE_AUTH,
    REQUIRE_REGULAR_AUTH,
    GetSessionFactory,
    GetUserDispatcher,
    GetUserStorage,
)
from hack_template.utils.users.dispatcher import UserDispatcher
from hack_template.utils.users.storage import UserStorage

ExceptionHandlersType = tuple[tuple[type[Exception], Callable], ...]


class REST(UvicornService):
    __required__ = (
        "debug",
        "title",
        "description",
        "version",
    )
    __dependencies__ = (
        "middlewares",
        "user_storage",
        "security_manager",
        "user_dispatcher",
    )

    EXCEPTION_HANDLERS: ExceptionHandlersType = (
        (HTTPException, http_exception_handler),
        (UserWithUsernameAlreadyExistsException, user_already_exists_handler),
        (HackTemplateException, internal_server_error_handler),
    )

    debug: bool
    title: str
    description: str
    version: str

    session_factory: async_sessionmaker[AsyncSession]
    security_manager: SecurityManager
    middlewares: Sequence[Middleware]
    user_storage: UserStorage
    user_dispatcher: UserDispatcher

    async def create_application(self) -> UvicornApplication:
        app = FastAPI(
            debug=self.debug,
            title=self.title,
            description=self.description,
            version=self.version,
        )
        self._add_middlewares(app)
        self._add_routes(app)
        self._add_exceptions(app)
        self._add_dependency_overrides(app)
        return app

    def _add_middlewares(self, app: FastAPI) -> None:
        for middleware in self.middlewares[::-1]:
            app.user_middleware.append(middleware)

    def _add_routes(self, app: FastAPI) -> None:
        app.include_router(api_router)

    def _add_exceptions(self, app: FastAPI) -> None:
        for exception, handler in self.EXCEPTION_HANDLERS:
            app.add_exception_handler(exception, handler)

    def _add_dependency_overrides(self, app: FastAPI) -> None:
        app.dependency_overrides.update(
            {
                MAYBE_AUTH: self.security_manager.maybe_auth,
                REQUIRE_AUTH: self.security_manager.require_auth,
                REQUIRE_ADMIN_AUTH: self.security_manager.require_admin_auth,
                REQUIRE_REGULAR_AUTH: self.security_manager.require_regular_auth,
                GetSessionFactory: lambda: self.session_factory,
                GetUserStorage: lambda: self.user_storage,
                GetUserDispatcher: lambda: self.user_dispatcher,
            }
        )