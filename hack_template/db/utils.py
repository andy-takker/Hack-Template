import abc
import os
from argparse import Namespace
from collections.abc import Callable, Coroutine
from enum import StrEnum
from functools import wraps
from pathlib import Path
from typing import Any, Concatenate, ParamSpec, TypeVar

import orjson
import sqlalchemy.dialects.postgresql as pg
from alembic.config import Config
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.ext.asyncio import (
    create_async_engine as sa_create_async_engine,
)

import hack_template
from hack_template.common.json import dumps

PROJECT_PATH = Path(hack_template.__file__).parent.parent.resolve()


class IStorage(abc.ABC):
    session_factory: async_sessionmaker[AsyncSession]


TClass = TypeVar("TClass", bound=IStorage)
TReturn = TypeVar("TReturn")
TParams = ParamSpec("TParams")

TFunc = Callable[
    Concatenate[TClass, TParams],
    Coroutine[Any, Any, TReturn],
]


def inject_session(func: TFunc) -> TFunc:
    @wraps(func)
    async def wrapper(
        self: TClass, *args: TParams.args, **kwargs: TParams.kwargs
    ) -> TReturn:
        if kwargs.get("session") is None:
            async with self.session_factory() as session:
                return await func(self, *args, **kwargs, session=session)
        else:
            return await func(self, *args, **kwargs)

    return wrapper


def create_async_engine(
    connection_uri: str,
    echo: bool = False,
    **engine_kwargs: Any,
) -> AsyncEngine:
    if engine_kwargs.get("json_serializer") is None:
        engine_kwargs["json_serializer"] = dumps
    if engine_kwargs.get("json_deserializer") is None:
        engine_kwargs["json_deserializer"] = orjson.loads
    return sa_create_async_engine(
        url=connection_uri,
        echo=echo,
        **engine_kwargs,
    )


def create_async_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


def make_alembic_config(cmd_opts: Namespace, base_path: Path = PROJECT_PATH) -> Config:
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = str(base_path / "hack_template/db" / cmd_opts.config)

    config = Config(
        file_=cmd_opts.config,
        ini_section=cmd_opts.name,
        cmd_opts=cmd_opts,
    )

    alembic_location = config.get_main_option("script_location")
    if not alembic_location:
        raise ValueError

    if not os.path.isabs(alembic_location):
        config.set_main_option("script_location", str(base_path / alembic_location))

    if cmd_opts.pg_dsn:
        config.set_main_option("sqlalchemy.url", cmd_opts.pg_dsn)

    config.attributes["configure_logger"] = False

    return config


def make_pg_enum(enum_cls: type[StrEnum], **kwargs: Any) -> pg.ENUM:
    return pg.ENUM(
        enum_cls,
        values_callable=_choices,
        **kwargs,
    )


def _choices(enum_cls: type[StrEnum]) -> tuple[str, ...]:
    return tuple(map(str, enum_cls))
