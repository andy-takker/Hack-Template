from base64 import b64decode

import argclass
from aiomisc_log import LogFormat, LogLevel
from yarl import URL


def load_base64(value: str) -> str:
    return b64decode(value).decode()


class SecurityGroup(argclass.Group):
    secret: str = argclass.Secret(
        "--secret", type=str, required=True, help="Secret key"
    )
    private_key: str = argclass.Secret(
        "--private-key", type=load_base64, required=True, help="Private key"
    )


class LogGroup(argclass.Group):
    level: LogLevel = argclass.EnumArgument(LogLevel, default=LogLevel.debug)
    format: LogFormat = argclass.EnumArgument(LogFormat, default=LogFormat.color)


class HostPortGroup(argclass.Group):
    host: str = argclass.Argument("--host", type=str, default="127.0.0.1")
    port: int = argclass.Argument("--port", type=int, default=8000)


class ProjectGroup(argclass.Group):
    title: str = argclass.Argument(
        "--title",
        type=str,
        default="REST service",
        help="Project title",
    )
    description = argclass.Argument(
        "--description",
        type=str,
        default="REST service",
        help="Project description",
    )
    version = argclass.Argument(
        "--version",
        type=str,
        default="1.0.0",
        help="Project version",
    )


class DatabaseGroup(argclass.Group):
    pg_dsn: URL = argclass.Argument("--pg-dsn", required=True, type=URL)


class RedisGroup(argclass.Group):
    redis_dsn: URL = argclass.Argument("--redis-dsn", required=True, type=URL)


class TelegramGroup(argclass.Group):
    bot_token: str = argclass.Secret("--bot-token", required=True, type=str)
