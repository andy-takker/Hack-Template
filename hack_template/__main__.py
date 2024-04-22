import logging

from aiomisc import Service, entrypoint

from hack_template.args import Parser
from hack_template.bot.service import TelegramBotService
from hack_template.deps import config_deps
from hack_template.rest.service import REST

log = logging.getLogger(__name__)


def main() -> None:
    parser = Parser(auto_env_var_prefix="APP_")
    parser.parse_args([])
    parser.sanitize_env()
    config_deps(parser)

    services: list[Service] = [
        REST(
            address=parser.http.host,
            port=parser.http.port,
            debug=parser.debug,
            title=parser.project.title,
            description=parser.project.description,
            version=parser.project.version,
        ),
        TelegramBotService(),
    ]

    with entrypoint(
        *services,
        log_level=parser.log.level,
        log_format=parser.log.format,
        pool_size=parser.pool_size,
        debug=parser.debug,
    ) as loop:
        log.info(
            "REST service started on address %s:%s",
            parser.http.host,
            parser.http.port,
        )
        loop.run_forever()


if __name__ == "__main__":
    main()
