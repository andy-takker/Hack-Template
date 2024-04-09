import argclass

from hack_template.utils.args import (
    DatabaseGroup,
    HostPortGroup,
    LogGroup,
    ProjectGroup,
    SecurityGroup,
)


class RESTParser(argclass.Parser):
    debug: bool = argclass.Argument(
        "-D",
        "--debug",
        action="store_true",
        default=False,
    )
    pool_size: int = argclass.Argument(
        "-s", "--pool-size", type=int, default=4, help="Thread pool size"
    )

    log = LogGroup(title="Logging options")
    http = HostPortGroup(title="HTTP options")
    project = ProjectGroup(title="Project options")
    db = DatabaseGroup(title="Database options")
    security = SecurityGroup(title="Security options")
